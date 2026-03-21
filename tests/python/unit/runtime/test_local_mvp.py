from __future__ import annotations

from typing import cast

import pytest

from verabrain.application import VeraBrainApplication
from verabrain.infrastructure import (
    OpenAIEmbeddingRuntimeSettings,
    PostgresRuntimeConfigurationError,
)
from verabrain.infrastructure.postgres_runtime import PostgresConnector
from verabrain.runtime.local_mvp import (
    LocalMVPStartupError,
    load_local_mvp_openai_embedding_settings,
    load_local_mvp_settings,
    main,
    run_local_mvp,
)


class FakeConnection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeMemoryEmbeddingProvider:
    def __init__(self, settings: OpenAIEmbeddingRuntimeSettings) -> None:
        self.settings = settings

    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return (0.1, 0.2) if text else None


def test_load_local_mvp_settings_prefers_dsn_configuration() -> None:
    settings = load_local_mvp_settings(
        {
            "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
            "VERABRAIN_POSTGRES_MIGRATION_MODE": "verify",
            "VERABRAIN_POSTGRES_FAIL_FAST": "false",
        }
    )

    assert settings.dsn == "postgresql://verabrain:test@localhost/verabrain"
    assert settings.connection_kwargs == {}
    assert settings.migration_mode == "verify"
    assert settings.fail_fast is False


def test_load_local_mvp_settings_supports_keyword_configuration() -> None:
    settings = load_local_mvp_settings(
        {
            "VERABRAIN_POSTGRES_HOST": "127.0.0.1",
            "VERABRAIN_POSTGRES_PORT": "5432",
            "VERABRAIN_POSTGRES_DB": "verabrain",
            "VERABRAIN_POSTGRES_USER": "verabrain",
            "VERABRAIN_POSTGRES_PASSWORD": "secret",
        }
    )

    assert settings.dsn is None
    assert settings.connection_kwargs == {
        "host": "127.0.0.1",
        "port": 5432,
        "dbname": "verabrain",
        "user": "verabrain",
        "password": "secret",
    }
    assert settings.migration_mode == "apply"
    assert settings.fail_fast is True


def test_load_local_mvp_settings_requires_complete_keyword_configuration() -> None:
    with pytest.raises(PostgresRuntimeConfigurationError, match="VERABRAIN_POSTGRES_DSN"):
        load_local_mvp_settings(
            {
                "VERABRAIN_POSTGRES_HOST": "127.0.0.1",
                "VERABRAIN_POSTGRES_DB": "verabrain",
            }
        )


def test_load_local_mvp_openai_embedding_settings_defaults_to_disabled() -> None:
    settings = load_local_mvp_openai_embedding_settings({})

    assert settings.enabled is False
    assert settings.api_key is None
    assert settings.model is None


def test_load_local_mvp_openai_embedding_settings_reads_explicit_configuration() -> None:
    settings = load_local_mvp_openai_embedding_settings(
        {
            "VERABRAIN_OPENAI_API_KEY": "test-key",
            "VERABRAIN_OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
            "VERABRAIN_OPENAI_BASE_URL": "https://example.test/v1",
        }
    )

    assert settings.enabled is True
    assert settings.api_key == "test-key"
    assert settings.model == "text-embedding-3-small"
    assert settings.base_url == "https://example.test/v1"


def test_run_local_mvp_bootstraps_schema_and_starts_stdio_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_connection = FakeConnection()
    bootstrap_calls: list[tuple[FakeConnection, object]] = []
    server_calls: list[tuple[VeraBrainApplication, str]] = []

    def fake_bootstrap_schema(connection: FakeConnection, *, settings: object) -> None:
        bootstrap_calls.append((connection, settings))

    def fake_run_stdio_server(
        application: VeraBrainApplication,
        *,
        server_name: str = "VeraBrain",
        server_factory=None,
    ) -> object:
        server_calls.append((application, server_name))
        return object()

    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.bootstrap_postgres_runtime_schema",
        fake_bootstrap_schema,
    )
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.run_stdio_server",
        fake_run_stdio_server,
    )
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.OpenAIEmbeddingProvider",
        FakeMemoryEmbeddingProvider,
    )

    exit_code = run_local_mvp(
        env={
            "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
            "VERABRAIN_POSTGRES_MIGRATION_MODE": "verify",
            "VERABRAIN_MCP_SERVER_NAME": "VeraBrain Local",
            "VERABRAIN_OPENAI_API_KEY": "test-key",
            "VERABRAIN_OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        },
        connector=cast(PostgresConnector, lambda *_args, **_kwargs: startup_connection),
    )

    assert exit_code == 0
    assert len(bootstrap_calls) == 1
    assert bootstrap_calls[0][0] is startup_connection
    assert server_calls[0][1] == "VeraBrain Local"
    assert server_calls[0][0].memory.memory_embedding_provider is not None
    assert startup_connection.closed is True


def test_run_local_mvp_keeps_memory_write_embeddings_disabled_without_openai_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_connection = FakeConnection()
    server_calls: list[tuple[VeraBrainApplication, str]] = []

    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.bootstrap_postgres_runtime_schema",
        lambda connection, *, settings: None,
    )
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.run_stdio_server",
        lambda application, *, server_name="VeraBrain", server_factory=None: server_calls.append(
            (application, server_name)
        ),
    )

    exit_code = run_local_mvp(
        env={
            "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
        },
        connector=cast(PostgresConnector, lambda *_args, **_kwargs: startup_connection),
    )

    assert exit_code == 0
    assert server_calls[0][0].memory.memory_embedding_provider is None


def test_run_local_mvp_fails_when_startup_connection_is_unavailable() -> None:
    with pytest.raises(LocalMVPStartupError, match="startup Postgres connection"):
        run_local_mvp(
            env={
                "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
                "VERABRAIN_POSTGRES_FAIL_FAST": "false",
            },
            connector=cast(
                PostgresConnector,
                lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("down")),
            ),
        )


def test_main_reports_startup_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.run_local_mvp",
        lambda: (_ for _ in ()).throw(LocalMVPStartupError("startup failed")),
    )

    result = main()

    captured = capsys.readouterr()
    assert result == 1
    assert captured.err.strip() == "startup failed"
