from __future__ import annotations

import pytest

from verabrain.infrastructure import (
    INITIAL_SCHEMA_MIGRATION,
    PostgresMigration,
    apply_postgres_migrations,
    list_postgres_migrations,
    render_postgres_migration_sql,
)


class FakeMigrationCursor:
    def __init__(self, connection: FakeMigrationConnection) -> None:
        self._connection = connection

    def execute(self, query: str) -> None:
        self._connection.executed.append(query)
        if self._connection.fail_on and self._connection.fail_on in query:
            raise RuntimeError("migration failed")

    def __enter__(self) -> FakeMigrationCursor:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool | None:
        return None


class FakeMigrationConnection:
    def __init__(self, *, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.executed: list[str] = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> FakeMigrationCursor:
        return FakeMigrationCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_migration_catalog_exposes_the_initial_schema_baseline() -> None:
    migrations = list_postgres_migrations()

    assert migrations == (INITIAL_SCHEMA_MIGRATION,)
    assert migrations[0].migration_id == "001_initial_schema"
    assert any("CREATE TABLE IF NOT EXISTS memories" in stmt for stmt in migrations[0].statements)


def test_render_postgres_migration_sql_includes_pgvector_and_domain_tables() -> None:
    rendered = render_postgres_migration_sql()

    assert "-- migration: 001_initial_schema" in rendered
    assert "CREATE EXTENSION IF NOT EXISTS vector;" in rendered
    assert "CREATE TABLE IF NOT EXISTS memories" in rendered
    assert "CREATE TABLE IF NOT EXISTS knowledge_items" in rendered
    assert "CREATE TABLE IF NOT EXISTS knowledge_links" in rendered
    assert "CREATE TABLE IF NOT EXISTS execution_items" in rendered
    assert "VECTOR(1536)" in rendered


def test_apply_postgres_migrations_executes_in_order_and_commits() -> None:
    connection = FakeMigrationConnection()
    custom = (
        PostgresMigration("001", "first", ("SELECT 1", "SELECT 2")),
        PostgresMigration("002", "second", ("SELECT 3",)),
    )

    applied = apply_postgres_migrations(connection, migrations=custom)

    assert applied == ("001", "002")
    assert connection.executed == ["SELECT 1", "SELECT 2", "SELECT 3"]
    assert connection.commits == 1
    assert connection.rollbacks == 0


def test_apply_postgres_migrations_rolls_back_on_failure() -> None:
    connection = FakeMigrationConnection(fail_on="SELECT 2")
    custom = (
        PostgresMigration("001", "broken", ("SELECT 1", "SELECT 2")),
    )

    with pytest.raises(RuntimeError, match="migration failed"):
        apply_postgres_migrations(connection, migrations=custom)

    assert connection.executed == ["SELECT 1", "SELECT 2"]
    assert connection.commits == 0
    assert connection.rollbacks == 1
