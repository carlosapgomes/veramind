"""Infrastructure adapters for persistence and external services."""

from .in_memory import (
    InMemoryExecutionRepository,
    InMemoryKnowledgeRepository,
    InMemoryMemoryRepository,
    InMemoryPersistenceStore,
    InMemoryUnitOfWork,
)
from .postgres_migrations import (
    INITIAL_SCHEMA_MIGRATION,
    PostgresMigration,
    apply_postgres_migrations,
    list_postgres_migrations,
    render_postgres_migration_sql,
)
from .postgres import (
    PostgresExecutionRepository,
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresUnitOfWork,
)
from .postgres_runtime import (
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

__all__ = [
    "InMemoryExecutionRepository",
    "InMemoryKnowledgeRepository",
    "InMemoryMemoryRepository",
    "InMemoryPersistenceStore",
    "InMemoryUnitOfWork",
    "INITIAL_SCHEMA_MIGRATION",
    "PostgresMigration",
    "PostgresExecutionRepository",
    "PostgresKnowledgeRepository",
    "PostgresMemoryRepository",
    "PostgresConnectionFactory",
    "PostgresConnectionUnavailableError",
    "PostgresDriverUnavailableError",
    "PostgresRuntimeApplicationFactory",
    "PostgresRuntimeBootstrapResult",
    "PostgresSchemaVerificationError",
    "PostgresUnitOfWork",
    "apply_postgres_migrations",
    "bootstrap_postgres_runtime_schema",
    "list_postgres_migrations",
    "load_default_postgres_connector",
    "PostgresRuntimeConfigurationError",
    "PostgresRuntimeSettings",
    "render_postgres_migration_sql",
    "verify_postgres_runtime_schema",
]
