from __future__ import annotations

from typing import Mapping, Sequence, cast

import pytest

from verabrain.infrastructure import (
    PostgresRuntimeApplicationFactory,
    PostgresRuntimeBootstrapResult,
    PostgresConnectionFactory,
    PostgresConnectionUnavailableError,
    PostgresDriverUnavailableError,
    PostgresRuntimeConfigurationError,
    PostgresSchemaVerificationError,
    PostgresRuntimeSettings,
    bootstrap_postgres_runtime_schema,
    load_default_postgres_connector,
    verify_postgres_runtime_schema,
)
from verabrain.application import SaveMemoryRequest
from verabrain.infrastructure import PostgresUnitOfWork
from verabrain.infrastructure.postgres_runtime import PostgresConnector

REQUIRED_RUNTIME_TARGETS = (
    "extension:vector",
    "relation:public.memories",
    "relation:public.memories_salience_updated_idx",
    "relation:public.memories_embedding_idx",
    "relation:public.knowledge_items",
    "relation:public.knowledge_items_updated_idx",
    "relation:public.knowledge_links",
    "relation:public.knowledge_links_left_idx",
    "relation:public.knowledge_links_right_idx",
    "relation:public.execution_items",
    "relation:public.execution_items_due_review_idx",
    "relation:public.execution_items_project_state_idx",
)


class FakeCursor:
    def __init__(self, connection: FakeConnection) -> None:
        self._connection = connection

    def execute(
        self,
        query: str,
        params: Mapping[str, object] | None = None,
    ) -> object:
        self._connection.executed.append((query, params))
        self._connection._last_params = params
        return None

    def fetchone(self) -> Mapping[str, object] | None:
        if self._connection._last_params is None:
            return None
        if "extension_name" in self._connection._last_params:
            extension = self._connection._last_params["extension_name"]
            return {"present": f"extension:{extension}" in self._connection.present_targets}
        if "qualified_name" in self._connection._last_params:
            qualified_name = self._connection._last_params["qualified_name"]
            return {"present": f"relation:{qualified_name}" in self._connection.present_targets}
        return None

    def fetchall(self) -> Sequence[Mapping[str, object]]:
        return []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool | None:
        return None


class FakeConnection:
    def __init__(self, *, present_targets: Sequence[str] = ()) -> None:
        self.present_targets = set(present_targets)
        self.executed: list[tuple[str, Mapping[str, object] | None]] = []
        self._last_params: Mapping[str, object] | None = None
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class RecordingConnector:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.connections: list[FakeConnection] = []

    def __call__(self, *args: object, **kwargs: object) -> FakeConnection:
        self.calls.append((args, dict(kwargs)))
        connection = FakeConnection()
        self.connections.append(connection)
        return connection


class SequenceConnector:
    def __init__(self, *results: FakeConnection | Exception) -> None:
        self._results = list(results)
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def __call__(self, *args: object, **kwargs: object) -> FakeConnection:
        self.calls.append((args, dict(kwargs)))
        if not self._results:
            raise AssertionError("No configured connector result remains.")
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_runtime_settings_require_connection_inputs() -> None:
    with pytest.raises(
        PostgresRuntimeConfigurationError,
        match="require a DSN or connection keyword arguments",
    ):
        PostgresRuntimeSettings(
            dsn="  ",
            migration_mode="apply",
            fail_fast=True,
        )


def test_runtime_settings_reject_unknown_migration_modes() -> None:
    with pytest.raises(
        PostgresRuntimeConfigurationError,
        match="must be one of: apply, verify, skip",
    ):
        PostgresRuntimeSettings(
            dsn="postgresql://verabrain:test@localhost/verabrain",
            migration_mode="drift-check",  # type: ignore[arg-type]
            fail_fast=True,
        )


def test_connection_factory_uses_explicit_runtime_settings() -> None:
    connector = RecordingConnector()
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
        connection_kwargs={"connect_timeout": 5, "application_name": "verabrain"},
    )
    factory = PostgresConnectionFactory(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    connection = factory.open_connection()

    assert isinstance(connection, FakeConnection)
    assert connector.calls == [
        (
            ("postgresql://verabrain:test@localhost/verabrain",),
            {"connect_timeout": 5, "application_name": "verabrain"},
        )
    ]
    assert factory.settings.migration_mode == "verify"


def test_connection_factory_supports_keyword_only_configuration() -> None:
    connector = RecordingConnector()
    settings = PostgresRuntimeSettings(
        migration_mode="skip",
        fail_fast=True,
        connection_kwargs={"host": "localhost", "dbname": "verabrain"},
    )
    factory = PostgresConnectionFactory(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    factory.open_connection()

    assert connector.calls == [((), {"host": "localhost", "dbname": "verabrain"})]


def test_startup_connection_raises_when_fail_fast_is_enabled() -> None:
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="apply",
        fail_fast=True,
    )
    factory = PostgresConnectionFactory(
        settings,
        connector=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("down")),
    )

    with pytest.raises(PostgresConnectionUnavailableError, match="Unable to create"):
        factory.open_startup_connection()


def test_startup_connection_returns_none_when_fail_fast_is_disabled() -> None:
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="apply",
        fail_fast=False,
    )
    factory = PostgresConnectionFactory(
        settings,
        connector=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("down")),
    )

    assert factory.open_startup_connection() is None


def test_loading_default_connector_reports_missing_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "verabrain.infrastructure.postgres_runtime.import_module",
        lambda _name: (_ for _ in ()).throw(ModuleNotFoundError("psycopg")),
    )

    with pytest.raises(PostgresDriverUnavailableError, match="psycopg is required"):
        load_default_postgres_connector()


def test_verify_postgres_runtime_schema_checks_required_runtime_artifacts() -> None:
    connection = FakeConnection(present_targets=REQUIRED_RUNTIME_TARGETS)

    verified = verify_postgres_runtime_schema(connection)

    assert verified[0] == "extension:vector"
    assert "relation:public.memories" in verified
    assert "relation:public.execution_items_project_state_idx" in verified
    assert connection.commits == 0
    assert connection.rollbacks == 0


def test_verify_postgres_runtime_schema_raises_for_missing_artifacts() -> None:
    connection = FakeConnection(
        present_targets=(
            "extension:vector",
            "relation:public.memories",
        )
    )

    with pytest.raises(
        PostgresSchemaVerificationError,
        match="relation:public.memories_salience_updated_idx",
    ):
        verify_postgres_runtime_schema(connection)


def test_bootstrap_postgres_runtime_schema_applies_migrations_before_verifying() -> None:
    connection = FakeConnection(present_targets=REQUIRED_RUNTIME_TARGETS)
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="apply",
        fail_fast=True,
    )

    result = bootstrap_postgres_runtime_schema(
        connection,
        settings=settings,
        migrations=(),
    )

    assert result == PostgresRuntimeBootstrapResult(
        migration_mode="apply",
        applied_migration_ids=("001_initial_schema",),
        verified_targets=result.verified_targets,
    )
    assert result.verified_targets[0] == "extension:vector"
    assert connection.commits == 1


def test_bootstrap_postgres_runtime_schema_verifies_without_apply_mode_side_effects() -> None:
    connection = FakeConnection(present_targets=REQUIRED_RUNTIME_TARGETS)
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
    )

    result = bootstrap_postgres_runtime_schema(connection, settings=settings)

    assert result.applied_migration_ids == ()
    assert result.migration_mode == "verify"
    assert connection.commits == 0
    assert connection.rollbacks == 0


def test_bootstrap_postgres_runtime_schema_skips_operational_handling_when_configured() -> None:
    connection = FakeConnection()
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="skip",
        fail_fast=True,
    )

    result = bootstrap_postgres_runtime_schema(connection, settings=settings)

    assert result == PostgresRuntimeBootstrapResult(migration_mode="skip")
    assert connection.executed == []
    assert connection.commits == 0
    assert connection.rollbacks == 0


def test_runtime_application_factory_creates_postgres_unit_of_work() -> None:
    connector = RecordingConnector()
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
    )
    factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    unit_of_work = factory.create_unit_of_work()

    assert isinstance(unit_of_work, PostgresUnitOfWork)
    assert factory.settings == settings
    assert connector.calls == [(("postgresql://verabrain:test@localhost/verabrain",), {})]


def test_runtime_application_factory_wires_postgres_backed_application() -> None:
    def provider(query: str) -> tuple[float, ...] | None:
        return (0.1, 0.2) if query == "Hermes" else None

    connector = RecordingConnector()
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
    )
    factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    application = factory.create_application(
        id_generator=lambda: "mem-1",
        memory_query_embedding_provider=provider,
    )
    saved = application.memory.save(
        SaveMemoryRequest(
            text="User prefers concise answers.",
            type="preference",
            scope="long",
            source="manual",
            salience=0.8,
        )
    )

    assert saved.id == "mem-1"
    assert application.context.memory_query_embedding_provider is provider
    assert len(connector.calls) == 1
    assert len(connector.connections) == 1
    assert connector.connections[0].commits == 1
    assert "INSERT INTO memories" in connector.connections[0].executed[0][0]


def test_wired_runtime_path_uses_separate_startup_and_application_connections() -> None:
    startup_connection = FakeConnection(present_targets=REQUIRED_RUNTIME_TARGETS)
    application_connection = FakeConnection()
    connector = SequenceConnector(startup_connection, application_connection)
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
    )
    factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    runtime_startup_connection = factory.connection_factory.open_startup_connection()
    assert runtime_startup_connection is not None
    result = bootstrap_postgres_runtime_schema(
        runtime_startup_connection,
        settings=factory.settings,
    )
    application = factory.create_application(id_generator=lambda: "mem-1")
    saved = application.memory.save(
        SaveMemoryRequest(
            text="User prefers concise answers.",
            type="preference",
            scope="long",
            source="manual",
            salience=0.8,
        )
    )

    assert runtime_startup_connection is startup_connection
    assert result == PostgresRuntimeBootstrapResult(
        migration_mode="verify",
        verified_targets=result.verified_targets,
    )
    assert saved.id == "mem-1"
    assert len(connector.calls) == 2
    assert startup_connection.commits == 0
    assert application_connection.commits == 1
    assert "SELECT EXISTS (" in startup_connection.executed[0][0]
    assert "INSERT INTO memories" in application_connection.executed[0][0]


def test_wired_runtime_path_reports_schema_failures_before_application_assembly() -> None:
    startup_connection = FakeConnection(
        present_targets=("extension:vector", "relation:public.memories")
    )
    application_connection = FakeConnection()
    connector = SequenceConnector(startup_connection, application_connection)
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=True,
    )
    factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    runtime_startup_connection = factory.connection_factory.open_startup_connection()
    assert runtime_startup_connection is not None

    with pytest.raises(
        PostgresSchemaVerificationError,
        match="relation:public.memories_salience_updated_idx",
    ):
        bootstrap_postgres_runtime_schema(
            runtime_startup_connection,
            settings=factory.settings,
        )

    assert runtime_startup_connection is startup_connection
    assert len(connector.calls) == 1
    assert startup_connection.commits == 0
    assert application_connection.executed == []


def test_wired_runtime_path_can_soft_fail_startup_before_later_application_use() -> None:
    application_connection = FakeConnection()
    connector = SequenceConnector(RuntimeError("database down"), application_connection)
    settings = PostgresRuntimeSettings(
        dsn="postgresql://verabrain:test@localhost/verabrain",
        migration_mode="verify",
        fail_fast=False,
    )
    factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=cast(PostgresConnector, connector),
    )

    startup_connection = factory.connection_factory.open_startup_connection()
    application = factory.create_application(id_generator=lambda: "mem-1")
    saved = application.memory.save(
        SaveMemoryRequest(
            text="Recovered after startup issue.",
            type="project",
            scope="medium",
            source="manual",
        )
    )

    assert startup_connection is None
    assert saved.id == "mem-1"
    assert len(connector.calls) == 2
    assert application_connection.commits == 1
    assert "INSERT INTO memories" in application_connection.executed[0][0]
