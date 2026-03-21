"""Local MVP launcher for the Postgres-backed VeraBrain MCP server."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from typing import Any, Protocol, cast

from verabrain.adapters.mcp import run_stdio_server
from verabrain.infrastructure import (
    OpenAIEmbeddingProvider,
    OpenAIEmbeddingRuntimeSettings,
    PostgresRuntimeApplicationFactory,
    PostgresRuntimeConfigurationError,
    PostgresRuntimeSettings,
    bootstrap_postgres_runtime_schema,
)
from verabrain.infrastructure.postgres_runtime import PostgresMigrationMode
from verabrain.infrastructure.postgres_runtime import PostgresConnectionProtocol
from verabrain.infrastructure.postgres_runtime import PostgresConnector

DEFAULT_SERVER_NAME = "VeraBrain"
DEFAULT_MIGRATION_MODE: PostgresMigrationMode = "apply"
DEFAULT_FAIL_FAST = True


class ClosableConnection(Protocol):
    """Minimal close behavior used for startup connections when available."""

    def close(self) -> None:
        ...


class LocalMVPStartupError(RuntimeError):
    """Raised when the local MVP launcher cannot start cleanly."""


def load_local_mvp_settings(
    env: Mapping[str, str] | None = None,
) -> PostgresRuntimeSettings:
    """Build explicit Postgres runtime settings for the local MVP path."""

    source = os.environ if env is None else env
    migration_mode = _parse_migration_mode(
        source.get("VERABRAIN_POSTGRES_MIGRATION_MODE")
    )
    fail_fast = _parse_bool(
        source.get("VERABRAIN_POSTGRES_FAIL_FAST"),
        default=DEFAULT_FAIL_FAST,
    )
    dsn = _clean(source.get("VERABRAIN_POSTGRES_DSN"))
    if dsn is not None:
        return PostgresRuntimeSettings(
            dsn=dsn,
            migration_mode=migration_mode,
            fail_fast=fail_fast,
        )

    return PostgresRuntimeSettings(
        migration_mode=migration_mode,
        fail_fast=fail_fast,
        connection_kwargs=_load_connection_kwargs(source),
    )


def run_local_mvp(
    *,
    env: Mapping[str, str] | None = None,
    connector: PostgresConnector | None = None,
    server_factory: Any | None = None,
) -> int:
    """Start the host-launched local MVP path over stdio."""

    source = os.environ if env is None else env
    settings = load_local_mvp_settings(source)
    embedding_settings = load_local_mvp_openai_embedding_settings(source)
    server_name = _clean(source.get("VERABRAIN_MCP_SERVER_NAME")) or DEFAULT_SERVER_NAME
    application_factory = PostgresRuntimeApplicationFactory.from_settings(
        settings,
        connector=connector,
    )
    startup_connection = application_factory.connection_factory.open_startup_connection()
    if startup_connection is None:
        raise LocalMVPStartupError(
            "The local MVP startup path could not obtain a startup Postgres connection."
        )

    try:
        bootstrap_postgres_runtime_schema(
            startup_connection,
            settings=settings,
        )
    finally:
        _close_connection(startup_connection)

    application = application_factory.create_application(
        memory_embedding_provider=_build_openai_memory_embedding_provider(
            embedding_settings
        )
    )
    run_stdio_server(
        application,
        server_name=server_name,
        server_factory=server_factory,
    )
    return 0


def main() -> int:
    """Console entrypoint for the local VeraBrain MVP launcher."""

    try:
        return run_local_mvp()
    except (LocalMVPStartupError, PostgresRuntimeConfigurationError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


def load_local_mvp_openai_embedding_settings(
    env: Mapping[str, str] | None = None,
) -> OpenAIEmbeddingRuntimeSettings:
    """Build explicit OpenAI embedding settings for the local MVP path."""

    source = os.environ if env is None else env
    return OpenAIEmbeddingRuntimeSettings(
        api_key=_clean(source.get("VERABRAIN_OPENAI_API_KEY")),
        model=_clean(source.get("VERABRAIN_OPENAI_EMBEDDING_MODEL")),
        base_url=_clean(source.get("VERABRAIN_OPENAI_BASE_URL")),
    )


def _load_connection_kwargs(env: Mapping[str, str]) -> dict[str, object]:
    required = {
        "host": _clean(env.get("VERABRAIN_POSTGRES_HOST")),
        "dbname": _clean(env.get("VERABRAIN_POSTGRES_DB")),
        "user": _clean(env.get("VERABRAIN_POSTGRES_USER")),
        "password": _clean(env.get("VERABRAIN_POSTGRES_PASSWORD")),
    }
    missing = sorted(key for key, value in required.items() if value is None)
    if missing:
        raise PostgresRuntimeConfigurationError(
            "The local MVP launcher requires VERABRAIN_POSTGRES_DSN or "
            "all of VERABRAIN_POSTGRES_HOST, VERABRAIN_POSTGRES_DB, "
            "VERABRAIN_POSTGRES_USER, and VERABRAIN_POSTGRES_PASSWORD."
        )

    kwargs: dict[str, object] = {key: value for key, value in required.items() if value}
    port = _clean(env.get("VERABRAIN_POSTGRES_PORT"))
    if port is not None:
        try:
            kwargs["port"] = int(port)
        except ValueError as exc:
            raise PostgresRuntimeConfigurationError(
                "VERABRAIN_POSTGRES_PORT must be an integer when provided."
            ) from exc
    return kwargs


def _parse_bool(value: str | None, *, default: bool) -> bool:
    normalized = _clean(value)
    if normalized is None:
        return default
    lowered = normalized.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    raise PostgresRuntimeConfigurationError(
        "VERABRAIN_POSTGRES_FAIL_FAST must be a boolean-like value when provided."
    )


def _parse_migration_mode(value: str | None) -> PostgresMigrationMode:
    normalized = _clean(value)
    if normalized is None:
        return DEFAULT_MIGRATION_MODE
    if normalized in {"apply", "verify", "skip"}:
        return cast(PostgresMigrationMode, normalized)
    raise PostgresRuntimeConfigurationError(
        "VERABRAIN_POSTGRES_MIGRATION_MODE must be one of: apply, verify, skip."
    )


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _close_connection(connection: PostgresConnectionProtocol) -> None:
    close = getattr(connection, "close", None)
    if callable(close):
        close()


def _build_openai_memory_embedding_provider(
    settings: OpenAIEmbeddingRuntimeSettings,
) -> OpenAIEmbeddingProvider | None:
    if not settings.enabled:
        return None
    return OpenAIEmbeddingProvider(settings)
