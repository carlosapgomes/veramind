"""Runtime settings and connection factory for the Postgres path."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import import_module
from typing import Callable, Literal, Mapping, Sequence, cast
from uuid import uuid4

from verabrain.application import (
    MemoryEmbeddingProvider,
    QueryEmbeddingProvider,
    VeraBrainApplication,
)

from .postgres import PostgresConnectionProtocol
from .postgres import PostgresUnitOfWork
from .postgres_migrations import (
    PostgresMigration,
    apply_postgres_migrations,
)

PostgresMigrationMode = Literal["apply", "verify", "skip"]
PostgresConnector = Callable[..., PostgresConnectionProtocol]

_VALID_MIGRATION_MODES = {"apply", "verify", "skip"}
_REQUIRED_RELATIONS = (
    "public.memories",
    "public.memories_salience_updated_idx",
    "public.memories_embedding_idx",
    "public.knowledge_items",
    "public.knowledge_items_updated_idx",
    "public.knowledge_links",
    "public.knowledge_links_left_idx",
    "public.knowledge_links_right_idx",
    "public.execution_items",
    "public.execution_items_due_review_idx",
    "public.execution_items_project_state_idx",
)
RuntimeClock = Callable[[], datetime]
RuntimeIdGenerator = Callable[[], str]


def _runtime_now() -> datetime:
    return datetime.now(tz=UTC)


def _runtime_id() -> str:
    return uuid4().hex


class PostgresRuntimeConfigurationError(ValueError):
    """Raised when runtime settings are incomplete or invalid."""


class PostgresDriverUnavailableError(RuntimeError):
    """Raised when the runtime cannot load the Postgres driver."""


class PostgresConnectionUnavailableError(RuntimeError):
    """Raised when the runtime cannot create a Postgres connection."""


class PostgresSchemaVerificationError(RuntimeError):
    """Raised when the configured schema state is not ready for runtime use."""


@dataclass(frozen=True, slots=True)
class PostgresRuntimeSettings:
    """Explicit operational settings for the Postgres runtime path."""

    migration_mode: PostgresMigrationMode
    fail_fast: bool
    dsn: str | None = None
    connection_kwargs: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_dsn = None if self.dsn is None else self.dsn.strip()
        normalized_kwargs = dict(self.connection_kwargs)
        if not normalized_dsn and not normalized_kwargs:
            raise PostgresRuntimeConfigurationError(
                "Postgres runtime settings require a DSN or connection keyword arguments."
            )
        if self.migration_mode not in _VALID_MIGRATION_MODES:
            raise PostgresRuntimeConfigurationError(
                "Postgres migration mode must be one of: apply, verify, skip."
            )
        object.__setattr__(self, "dsn", normalized_dsn or None)
        object.__setattr__(self, "connection_kwargs", normalized_kwargs)

    def connector_call(self) -> tuple[tuple[object, ...], dict[str, object]]:
        """Return the positional and keyword arguments for the driver."""

        kwargs = dict(self.connection_kwargs)
        if self.dsn is None:
            return (), kwargs
        return (self.dsn,), kwargs


def load_default_postgres_connector() -> PostgresConnector:
    """Load the default psycopg connection callable lazily."""

    try:
        psycopg = import_module("psycopg")
    except ModuleNotFoundError as exc:
        raise PostgresDriverUnavailableError(
            "psycopg is required for the Postgres runtime path."
        ) from exc
    try:
        pgvector_psycopg = import_module("pgvector.psycopg")
    except ModuleNotFoundError as exc:
        raise PostgresDriverUnavailableError(
            "pgvector is required for the Postgres runtime path."
        ) from exc
    connect = getattr(psycopg, "connect", None)
    if not callable(connect):
        raise PostgresDriverUnavailableError(
            "psycopg.connect is not available for the Postgres runtime path."
        )
    register_vector = getattr(pgvector_psycopg, "register_vector", None)
    if not callable(register_vector):
        raise PostgresDriverUnavailableError(
            "pgvector.psycopg.register_vector is required for the Postgres runtime path."
        )
    rows = getattr(psycopg, "rows", None)
    dict_row = getattr(rows, "dict_row", None)

    def connector(*args: object, **kwargs: object) -> PostgresConnectionProtocol:
        connection_kwargs = dict(kwargs)
        if dict_row is not None and "row_factory" not in connection_kwargs:
            connection_kwargs["row_factory"] = dict_row
        connection = cast(
            PostgresConnectionProtocol,
            connect(*args, **connection_kwargs),
        )
        register_vector(connection)
        return connection

    return connector


class PostgresConnectionFactory:
    """Construct Postgres connections from explicit runtime settings."""

    def __init__(
        self,
        settings: PostgresRuntimeSettings,
        *,
        connector: PostgresConnector | None = None,
    ) -> None:
        self._settings = settings
        self._connector = connector

    @property
    def settings(self) -> PostgresRuntimeSettings:
        """Expose the operational settings used by this factory."""

        return self._settings

    def open_connection(self) -> PostgresConnectionProtocol:
        """Create a Postgres connection or raise an operational error."""

        connector = self._connector or load_default_postgres_connector()
        args, kwargs = self._settings.connector_call()
        try:
            return connector(*args, **kwargs)
        except PostgresDriverUnavailableError:
            raise
        except Exception as exc:
            raise PostgresConnectionUnavailableError(
                "Unable to create a Postgres connection for the configured runtime path."
            ) from exc

    def open_startup_connection(self) -> PostgresConnectionProtocol | None:
        """Open a startup connection, honoring the configured failure policy."""

        try:
            return self.open_connection()
        except (PostgresDriverUnavailableError, PostgresConnectionUnavailableError):
            if self._settings.fail_fast:
                raise
            return None


@dataclass(frozen=True, slots=True)
class PostgresRuntimeBootstrapResult:
    """Observable result for runtime schema bootstrap handling."""

    migration_mode: PostgresMigrationMode
    applied_migration_ids: tuple[str, ...] = ()
    verified_targets: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PostgresRuntimeApplicationFactory:
    """Infrastructure factory for the Postgres-backed VeraBrain application."""

    connection_factory: PostgresConnectionFactory

    @classmethod
    def from_settings(
        cls,
        settings: PostgresRuntimeSettings,
        *,
        connector: PostgresConnector | None = None,
    ) -> PostgresRuntimeApplicationFactory:
        """Construct the application factory from explicit runtime settings."""

        return cls(
            connection_factory=PostgresConnectionFactory(
                settings,
                connector=connector,
            )
        )

    @property
    def settings(self) -> PostgresRuntimeSettings:
        """Expose the runtime settings behind this application factory."""

        return self.connection_factory.settings

    def create_unit_of_work(self) -> PostgresUnitOfWork:
        """Construct a Postgres-backed unit of work for application wiring."""

        return PostgresUnitOfWork(
            connection_factory=self.connection_factory.open_connection,
        )

    def create_application(
        self,
        *,
        clock: RuntimeClock | None = None,
        id_generator: RuntimeIdGenerator | None = None,
        memory_embedding_provider: MemoryEmbeddingProvider | None = None,
        memory_query_embedding_provider: QueryEmbeddingProvider | None = None,
    ) -> VeraBrainApplication:
        """Construct the VeraBrain application over the Postgres path."""

        return VeraBrainApplication(
            unit_of_work=self.create_unit_of_work(),
            clock=clock if clock is not None else _runtime_now,
            id_generator=id_generator if id_generator is not None else _runtime_id,
            memory_embedding_provider=memory_embedding_provider,
            memory_query_embedding_provider=memory_query_embedding_provider,
        )


def verify_postgres_runtime_schema(
    connection: PostgresConnectionProtocol,
) -> tuple[str, ...]:
    """Verify the required Postgres runtime artifacts are available."""

    verified = [_verify_pgvector_extension(connection)]
    verified.extend(_verify_relation(connection, name) for name in _REQUIRED_RELATIONS)
    return tuple(verified)


def bootstrap_postgres_runtime_schema(
    connection: PostgresConnectionProtocol,
    *,
    settings: PostgresRuntimeSettings,
    migrations: Sequence[PostgresMigration] | None = None,
) -> PostgresRuntimeBootstrapResult:
    """Apply, verify, or intentionally skip runtime schema handling."""

    if settings.migration_mode == "skip":
        return PostgresRuntimeBootstrapResult(migration_mode="skip")

    applied: tuple[str, ...] = ()
    if settings.migration_mode == "apply":
        applied = apply_postgres_migrations(connection, migrations=migrations)

    verified = verify_postgres_runtime_schema(connection)
    return PostgresRuntimeBootstrapResult(
        migration_mode=settings.migration_mode,
        applied_migration_ids=applied,
        verified_targets=verified,
    )


def _verify_pgvector_extension(connection: PostgresConnectionProtocol) -> str:
    query = """
        SELECT EXISTS (
          SELECT 1
          FROM pg_extension
          WHERE extname = %(extension_name)s
        ) AS present
    """
    _ensure_present(
        connection,
        query,
        {"extension_name": "vector"},
        target="extension:vector",
    )
    return "extension:vector"


def _verify_relation(
    connection: PostgresConnectionProtocol,
    qualified_name: str,
) -> str:
    query = """
        SELECT to_regclass(%(qualified_name)s) IS NOT NULL AS present
    """
    _ensure_present(
        connection,
        query,
        {"qualified_name": qualified_name},
        target=f"relation:{qualified_name}",
    )
    return f"relation:{qualified_name}"


def _ensure_present(
    connection: PostgresConnectionProtocol,
    query: str,
    params: Mapping[str, object],
    *,
    target: str,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
    if not _row_has_present(row):
        raise PostgresSchemaVerificationError(
            f"Postgres runtime schema verification failed for {target}."
        )


def _row_has_present(row: object) -> bool:
    if row is None:
        return False
    if isinstance(row, Mapping):
        return row.get("present") is True
    if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)):
        return len(row) > 0 and row[0] is True
    return False
