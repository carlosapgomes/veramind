"""Migration assets and helpers for the Postgres persistence path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence


class MigrationCursorProtocol(Protocol):
    """Minimal cursor protocol needed for migration execution."""

    def execute(self, query: str) -> object:
        ...

    def __enter__(self) -> MigrationCursorProtocol:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool | None:
        ...


class MigrationConnectionProtocol(Protocol):
    """Minimal connection protocol needed for migration execution."""

    def cursor(self) -> MigrationCursorProtocol:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


@dataclass(frozen=True, slots=True)
class PostgresMigration:
    """Ordered migration definition for the Postgres persistence path."""

    migration_id: str
    description: str
    statements: tuple[str, ...]


INITIAL_SCHEMA_MIGRATION = PostgresMigration(
    migration_id="001_initial_schema",
    description="Create the baseline VeraBrain Postgres and pgvector schema.",
    statements=(
        """
        CREATE EXTENSION IF NOT EXISTS vector
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS memories (
          id TEXT PRIMARY KEY,
          text TEXT NOT NULL,
          type TEXT NOT NULL,
          scope TEXT NOT NULL,
          salience DOUBLE PRECISION NOT NULL,
          created_at TIMESTAMPTZ NOT NULL,
          updated_at TIMESTAMPTZ NOT NULL,
          last_used_at TIMESTAMPTZ NULL,
          source TEXT NOT NULL,
          embedding VECTOR(1536) NULL,
          metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS memories_salience_updated_idx
          ON memories (salience DESC, updated_at DESC)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS memories_embedding_idx
          ON memories USING ivfflat (embedding vector_cosine_ops)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS knowledge_items (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          text TEXT NOT NULL,
          kind TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL,
          updated_at TIMESTAMPTZ NOT NULL,
          source TEXT NOT NULL,
          metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS knowledge_items_updated_idx
          ON knowledge_items (updated_at DESC)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS knowledge_links (
          id TEXT PRIMARY KEY,
          left_id TEXT NOT NULL REFERENCES knowledge_items(id),
          right_id TEXT NOT NULL REFERENCES knowledge_items(id),
          relation TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL,
          metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS knowledge_links_left_idx
          ON knowledge_links (left_id, created_at DESC)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS knowledge_links_right_idx
          ON knowledge_links (right_id, created_at DESC)
        """.strip(),
        """
        CREATE TABLE IF NOT EXISTS execution_items (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          kind TEXT NOT NULL,
          state TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL,
          updated_at TIMESTAMPTZ NOT NULL,
          source TEXT NOT NULL,
          project_id TEXT NULL,
          due_at TIMESTAMPTZ NULL,
          review_at TIMESTAMPTZ NULL,
          metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        )
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS execution_items_due_review_idx
          ON execution_items (due_at, review_at, updated_at DESC)
        """.strip(),
        """
        CREATE INDEX IF NOT EXISTS execution_items_project_state_idx
          ON execution_items (project_id, state, updated_at DESC)
        """.strip(),
    ),
)

POSTGRES_MIGRATIONS = (INITIAL_SCHEMA_MIGRATION,)


def list_postgres_migrations() -> tuple[PostgresMigration, ...]:
    """Return the ordered migration catalog for the Postgres path."""

    return POSTGRES_MIGRATIONS


def apply_postgres_migrations(
    connection: MigrationConnectionProtocol,
    *,
    migrations: Sequence[PostgresMigration] | None = None,
) -> tuple[str, ...]:
    """Apply the selected migrations inside one explicit transaction."""

    applied: list[str] = []
    selected = tuple(migrations or POSTGRES_MIGRATIONS)
    try:
        with connection.cursor() as cursor:
            for migration in selected:
                for statement in migration.statements:
                    cursor.execute(statement)
                applied.append(migration.migration_id)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return tuple(applied)


def render_postgres_migration_sql(
    migrations: Iterable[PostgresMigration] | None = None,
) -> str:
    """Render the selected migrations as one SQL artifact string."""

    selected = tuple(migrations or POSTGRES_MIGRATIONS)
    blocks: list[str] = []
    for migration in selected:
        blocks.append(f"-- migration: {migration.migration_id}")
        blocks.extend(f"{statement.strip()};" for statement in migration.statements)
    return "\n\n".join(blocks)
