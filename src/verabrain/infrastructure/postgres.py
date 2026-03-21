"""Postgres-backed infrastructure adapters for VeraBrain persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Mapping, Protocol, Sequence

from psycopg.types.json import Jsonb

from verabrain.application import (
    ExecutionQuery,
    ExecutionRecord,
    ExecutionRepository,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeRepository,
    KnowledgeSearchQuery,
    MemoryRecord,
    MemoryRepository,
    MemorySearchQuery,
    PersistenceUnitOfWork,
)
from verabrain.core import (
    MemoryRetrievalCandidate,
    memory_candidate_limit,
    rerank_memory_candidates,
)

Row = Mapping[str, object]
Parameters = Mapping[str, object]


class PostgresCursorProtocol(Protocol):
    """Minimal cursor protocol needed by the Postgres adapters."""

    def execute(self, query: str, params: Parameters | None = None) -> object:
        ...

    def fetchone(self) -> Row | None:
        ...

    def fetchall(self) -> Sequence[Row]:
        ...

    def __enter__(self) -> PostgresCursorProtocol:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool | None:
        ...


class PostgresConnectionProtocol(Protocol):
    """Minimal connection protocol needed by the Postgres adapters."""

    def cursor(self) -> PostgresCursorProtocol:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


ConnectionFactory = Callable[[], PostgresConnectionProtocol]


class PostgresMemoryRepository(MemoryRepository):
    """Postgres implementation of the memory repository port."""

    def __init__(self, connection: PostgresConnectionProtocol) -> None:
        self._connection = connection

    def get(self, record_id: str) -> MemoryRecord | None:
        query = """
            SELECT
              id,
              text,
              type,
              scope,
              salience,
              created_at,
              updated_at,
              last_used_at,
              source,
              embedding,
              metadata
            FROM memories
            WHERE id = %(record_id)s
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, {"record_id": record_id})
            row = cursor.fetchone()
        return None if row is None else _row_to_memory_record(row)

    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        query = """
            INSERT INTO memories (
              id,
              text,
              type,
              scope,
              salience,
              created_at,
              updated_at,
              last_used_at,
              source,
              embedding,
              metadata
            ) VALUES (
              %(id)s,
              %(text)s,
              %(type)s,
              %(scope)s,
              %(salience)s,
              %(created_at)s,
              %(updated_at)s,
              %(last_used_at)s,
              %(source)s,
              %(embedding)s,
              %(metadata)s
            )
            ON CONFLICT (id) DO UPDATE SET
              text = EXCLUDED.text,
              type = EXCLUDED.type,
              scope = EXCLUDED.scope,
              salience = EXCLUDED.salience,
              updated_at = EXCLUDED.updated_at,
              last_used_at = EXCLUDED.last_used_at,
              source = EXCLUDED.source,
              embedding = EXCLUDED.embedding,
              metadata = EXCLUDED.metadata
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, _memory_record_params(record))
        return record

    def find_similar(self, *, text: str, limit: int = 5) -> Sequence[MemoryRecord]:
        rows = self._fetch_memory_candidate_rows(
            text=text,
            limit=limit,
            min_salience=None,
            query_embedding=None,
        )
        return _rerank_memory_rows(rows, query_text=text, limit=limit)

    def search(self, query: MemorySearchQuery) -> Sequence[MemoryRecord]:
        rows = self._fetch_memory_candidate_rows(
            text=query.text,
            limit=query.limit,
            min_salience=query.min_salience,
            query_embedding=query.query_embedding,
        )
        return _rerank_memory_rows(rows, query_text=query.text, limit=query.limit)

    def _fetch_memory_candidate_rows(
        self,
        *,
        text: str,
        limit: int,
        min_salience: float | None,
        query_embedding: tuple[float, ...] | None,
    ) -> Sequence[Row]:
        if query_embedding is None:
            return self._fetch_lexical_memory_candidate_rows(
                text=text,
                limit=limit,
                min_salience=min_salience,
            )
        return self._fetch_semantic_memory_candidate_rows(
            text=text,
            limit=limit,
            min_salience=min_salience,
            query_embedding=query_embedding,
        )

    def _fetch_lexical_memory_candidate_rows(
        self,
        *,
        text: str,
        limit: int,
        min_salience: float | None,
    ) -> Sequence[Row]:
        where_clauses = ["text ILIKE %(pattern)s"]
        params: dict[str, object] = {
            "pattern": _like_pattern(text),
            "candidate_limit": memory_candidate_limit(limit),
        }
        if min_salience is not None:
            where_clauses.append("salience >= %(min_salience)s")
            params["min_salience"] = min_salience
        sql = """
            SELECT
              id,
              text,
              type,
              scope,
              salience,
              created_at,
              updated_at,
              last_used_at,
              source,
              embedding,
              metadata,
              CASE
                WHEN text ILIKE %(pattern)s THEN 1.0
                ELSE 0.0
              END AS lexical_score,
              NULL AS semantic_score
            FROM memories
            WHERE {where_clause}
            ORDER BY salience DESC, updated_at DESC, id ASC
            LIMIT %(candidate_limit)s
        """.format(where_clause="\n              AND ".join(where_clauses))
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def _fetch_semantic_memory_candidate_rows(
        self,
        *,
        text: str,
        limit: int,
        min_salience: float | None,
        query_embedding: tuple[float, ...],
    ) -> Sequence[Row]:
        where_clauses = ["(text ILIKE %(pattern)s OR embedding IS NOT NULL)"]
        params: dict[str, object] = {
            "pattern": _like_pattern(text),
            "query_embedding": _vector_literal(query_embedding),
            "candidate_limit": memory_candidate_limit(limit),
        }
        if min_salience is not None:
            where_clauses.append("salience >= %(min_salience)s")
            params["min_salience"] = min_salience
        sql = """
            SELECT
              id,
              text,
              type,
              scope,
              salience,
              created_at,
              updated_at,
              last_used_at,
              source,
              embedding,
              metadata,
              CASE
                WHEN text ILIKE %(pattern)s THEN 1.0
                ELSE 0.0
              END AS lexical_score,
              CASE
                WHEN embedding IS NULL THEN NULL
                ELSE 1 - (embedding <=> %(query_embedding)s::vector)
              END AS semantic_score
            FROM memories
            WHERE {where_clause}
            ORDER BY
              CASE WHEN embedding IS NULL THEN NULL
                ELSE embedding <=> %(query_embedding)s::vector
              END ASC NULLS LAST,
              salience DESC,
              updated_at DESC,
              id ASC
            LIMIT %(candidate_limit)s
        """.format(where_clause="\n              AND ".join(where_clauses))
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


class PostgresKnowledgeRepository(KnowledgeRepository):
    """Postgres implementation of the knowledge repository port."""

    def __init__(self, connection: PostgresConnectionProtocol) -> None:
        self._connection = connection

    def get(self, record_id: str) -> KnowledgeRecord | None:
        query = """
            SELECT
              id,
              title,
              text,
              kind,
              created_at,
              updated_at,
              source,
              metadata
            FROM knowledge_items
            WHERE id = %(record_id)s
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, {"record_id": record_id})
            row = cursor.fetchone()
        return None if row is None else _row_to_knowledge_record(row)

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        query = """
            INSERT INTO knowledge_items (
              id,
              title,
              text,
              kind,
              created_at,
              updated_at,
              source,
              metadata
            ) VALUES (
              %(id)s,
              %(title)s,
              %(text)s,
              %(kind)s,
              %(created_at)s,
              %(updated_at)s,
              %(source)s,
              %(metadata)s
            )
            ON CONFLICT (id) DO UPDATE SET
              title = EXCLUDED.title,
              text = EXCLUDED.text,
              kind = EXCLUDED.kind,
              updated_at = EXCLUDED.updated_at,
              source = EXCLUDED.source,
              metadata = EXCLUDED.metadata
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, _knowledge_record_params(record))
        return record

    def search(self, query: KnowledgeSearchQuery) -> Sequence[KnowledgeRecord]:
        clauses = ["(title ILIKE %(pattern)s OR text ILIKE %(pattern)s)"]
        params: dict[str, object] = {
            "pattern": _like_pattern(query.text),
            "limit": query.limit,
        }
        if query.related_to is not None:
            clauses.append(
                """
                EXISTS (
                  SELECT 1
                  FROM knowledge_links kl
                  WHERE (
                    kl.left_id = knowledge_items.id
                    AND kl.right_id = %(related_to)s
                  ) OR (
                    kl.right_id = knowledge_items.id
                    AND kl.left_id = %(related_to)s
                  )
                )
                """
            )
            params["related_to"] = query.related_to

        sql = f"""
            SELECT
              id,
              title,
              text,
              kind,
              created_at,
              updated_at,
              source,
              metadata
            FROM knowledge_items
            WHERE {' AND '.join(clause.strip() for clause in clauses)}
            ORDER BY updated_at DESC, id ASC
            LIMIT %(limit)s
        """
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return [_row_to_knowledge_record(row) for row in rows]

    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        query = """
            INSERT INTO knowledge_links (
              id,
              left_id,
              right_id,
              relation,
              created_at,
              metadata
            ) VALUES (
              %(id)s,
              %(left_id)s,
              %(right_id)s,
              %(relation)s,
              %(created_at)s,
              %(metadata)s
            )
            ON CONFLICT (id) DO UPDATE SET
              left_id = EXCLUDED.left_id,
              right_id = EXCLUDED.right_id,
              relation = EXCLUDED.relation,
              metadata = EXCLUDED.metadata
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, _knowledge_link_params(link))
        return link

    def list_links(self, record_id: str) -> Sequence[KnowledgeLinkRecord]:
        query = """
            SELECT
              id,
              left_id,
              right_id,
              relation,
              created_at,
              metadata
            FROM knowledge_links
            WHERE left_id = %(record_id)s OR right_id = %(record_id)s
            ORDER BY created_at DESC, id ASC
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, {"record_id": record_id})
            rows = cursor.fetchall()
        return [_row_to_knowledge_link_record(row) for row in rows]


class PostgresExecutionRepository(ExecutionRepository):
    """Postgres implementation of the execution repository port."""

    def __init__(self, connection: PostgresConnectionProtocol) -> None:
        self._connection = connection

    def get(self, record_id: str) -> ExecutionRecord | None:
        query = """
            SELECT
              id,
              title,
              kind,
              state,
              created_at,
              updated_at,
              source,
              project_id,
              due_at,
              review_at,
              metadata
            FROM execution_items
            WHERE id = %(record_id)s
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, {"record_id": record_id})
            row = cursor.fetchone()
        return None if row is None else _row_to_execution_record(row)

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        query = """
            INSERT INTO execution_items (
              id,
              title,
              kind,
              state,
              created_at,
              updated_at,
              source,
              project_id,
              due_at,
              review_at,
              metadata
            ) VALUES (
              %(id)s,
              %(title)s,
              %(kind)s,
              %(state)s,
              %(created_at)s,
              %(updated_at)s,
              %(source)s,
              %(project_id)s,
              %(due_at)s,
              %(review_at)s,
              %(metadata)s
            )
            ON CONFLICT (id) DO UPDATE SET
              title = EXCLUDED.title,
              kind = EXCLUDED.kind,
              state = EXCLUDED.state,
              updated_at = EXCLUDED.updated_at,
              source = EXCLUDED.source,
              project_id = EXCLUDED.project_id,
              due_at = EXCLUDED.due_at,
              review_at = EXCLUDED.review_at,
              metadata = EXCLUDED.metadata
        """
        with self._connection.cursor() as cursor:
            cursor.execute(query, _execution_record_params(record))
        return record

    def search(self, query: ExecutionQuery) -> Sequence[ExecutionRecord]:
        clauses = ["TRUE"]
        params: dict[str, object] = {"limit": query.limit}
        if query.states:
            clauses.append("state = ANY(%(states)s)")
            params["states"] = list(query.states)
        if query.project_id is not None:
            clauses.append("project_id = %(project_id)s")
            params["project_id"] = query.project_id
        if query.due_before is not None:
            clauses.append("due_at <= %(due_before)s")
            params["due_before"] = query.due_before
        if query.review_before is not None:
            clauses.append("review_at <= %(review_before)s")
            params["review_before"] = query.review_before

        sql = f"""
            SELECT
              id,
              title,
              kind,
              state,
              created_at,
              updated_at,
              source,
              project_id,
              due_at,
              review_at,
              metadata
            FROM execution_items
            WHERE {' AND '.join(clauses)}
            ORDER BY due_at NULLS LAST, review_at NULLS LAST, updated_at DESC, id ASC
            LIMIT %(limit)s
        """
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return [_row_to_execution_record(row) for row in rows]

    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> Sequence[ExecutionRecord]:
        query = """
            SELECT
              id,
              title,
              kind,
              state,
              created_at,
              updated_at,
              source,
              project_id,
              due_at,
              review_at,
              metadata
            FROM execution_items
            WHERE review_at IS NOT NULL
              AND review_at <= %(reference_at)s
            ORDER BY review_at ASC, updated_at DESC, id ASC
            LIMIT %(limit)s
        """
        params = {"reference_at": reference_at, "limit": limit}
        with self._connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return [_row_to_execution_record(row) for row in rows]


class PostgresUnitOfWork(PersistenceUnitOfWork):
    """Postgres-backed unit of work over a single connection."""

    def __init__(self, *, connection_factory: ConnectionFactory) -> None:
        self._connection = connection_factory()
        self._memories = PostgresMemoryRepository(self._connection)
        self._knowledge = PostgresKnowledgeRepository(self._connection)
        self._execution = PostgresExecutionRepository(self._connection)

    @property
    def memories(self) -> MemoryRepository:
        return self._memories

    @property
    def knowledge(self) -> KnowledgeRepository:
        return self._knowledge

    @property
    def execution(self) -> ExecutionRepository:
        return self._execution

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()


def _memory_record_params(record: MemoryRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "text": record.text,
        "type": record.type,
        "scope": record.scope,
        "salience": record.salience,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "last_used_at": record.last_used_at,
        "source": record.source,
        "embedding": list(record.embedding) if record.embedding else None,
        "metadata": _jsonb_metadata(record.metadata),
    }


def _knowledge_record_params(record: KnowledgeRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "title": record.title,
        "text": record.text,
        "kind": record.kind,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "source": record.source,
        "metadata": _jsonb_metadata(record.metadata),
    }


def _knowledge_link_params(link: KnowledgeLinkRecord) -> dict[str, object]:
    return {
        "id": link.id,
        "left_id": link.left_id,
        "right_id": link.right_id,
        "relation": link.relation,
        "created_at": link.created_at,
        "metadata": _jsonb_metadata(link.metadata),
    }


def _execution_record_params(record: ExecutionRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "title": record.title,
        "kind": record.kind,
        "state": record.state,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "source": record.source,
        "project_id": record.project_id,
        "due_at": record.due_at,
        "review_at": record.review_at,
        "metadata": _jsonb_metadata(record.metadata),
    }


def _jsonb_metadata(metadata: Mapping[str, object]) -> Jsonb:
    return Jsonb(dict(metadata))


def _row_to_memory_record(row: Row) -> MemoryRecord:
    return MemoryRecord(
        id=_require_str(row, "id"),
        text=_require_str(row, "text"),
        type=_require_str(row, "type"),
        scope=_require_str(row, "scope"),
        salience=_require_float(row, "salience"),
        created_at=_require_datetime(row, "created_at"),
        updated_at=_require_datetime(row, "updated_at"),
        last_used_at=_optional_datetime(row, "last_used_at"),
        source=_require_str(row, "source"),
        embedding=_optional_embedding(row.get("embedding")),
        metadata=_optional_metadata(row.get("metadata")),
    )


def _row_to_knowledge_record(row: Row) -> KnowledgeRecord:
    return KnowledgeRecord(
        id=_require_str(row, "id"),
        title=_require_str(row, "title"),
        text=_require_str(row, "text"),
        kind=_require_str(row, "kind"),
        created_at=_require_datetime(row, "created_at"),
        updated_at=_require_datetime(row, "updated_at"),
        source=_require_str(row, "source"),
        metadata=_optional_metadata(row.get("metadata")),
    )


def _row_to_knowledge_link_record(row: Row) -> KnowledgeLinkRecord:
    return KnowledgeLinkRecord(
        id=_require_str(row, "id"),
        left_id=_require_str(row, "left_id"),
        right_id=_require_str(row, "right_id"),
        relation=_require_str(row, "relation"),
        created_at=_require_datetime(row, "created_at"),
        metadata=_optional_metadata(row.get("metadata")),
    )


def _row_to_execution_record(row: Row) -> ExecutionRecord:
    return ExecutionRecord(
        id=_require_str(row, "id"),
        title=_require_str(row, "title"),
        kind=_require_str(row, "kind"),
        state=_require_str(row, "state"),
        created_at=_require_datetime(row, "created_at"),
        updated_at=_require_datetime(row, "updated_at"),
        source=_require_str(row, "source"),
        project_id=_optional_str(row.get("project_id"), "project_id"),
        due_at=_optional_datetime(row, "due_at"),
        review_at=_optional_datetime(row, "review_at"),
        metadata=_optional_metadata(row.get("metadata")),
    )


def _require_str(row: Row, key: str) -> str:
    value = row.get(key)
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected '{key}' to be a string in the database row")


def _optional_str(value: object, key: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected '{key}' to be a string or null in the database row")


def _require_float(row: Row, key: str) -> float:
    value = row.get(key)
    if isinstance(value, int | float):
        return float(value)
    raise ValueError(f"Expected '{key}' to be numeric in the database row")


def _require_datetime(row: Row, key: str) -> datetime:
    value = row.get(key)
    if not isinstance(value, datetime):
        raise ValueError(f"Expected '{key}' to be a datetime in the database row")
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _optional_datetime(row: Row, key: str) -> datetime | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, datetime):
        raise ValueError(f"Expected '{key}' to be a datetime or null in the database row")
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _optional_embedding(value: object) -> tuple[float, ...] | None:
    if value is None:
        return None
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return tuple(float(item) for item in value)
    raise ValueError("Expected 'embedding' to be a numeric sequence or null")


def _optional_metadata(value: object) -> Mapping[str, object]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(key): nested for key, nested in value.items()}
    raise ValueError("Expected 'metadata' to be an object or null")


def _like_pattern(value: str) -> str:
    return f"%{' '.join(value.split())}%"


def _vector_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _rerank_memory_rows(
    rows: Sequence[Row],
    *,
    query_text: str,
    limit: int,
) -> list[MemoryRecord]:
    candidates = tuple(_row_to_memory_candidate(row) for row in rows)
    return list(
        rerank_memory_candidates(candidates, query_text=query_text, limit=limit)
    )


def _row_to_memory_candidate(row: Row) -> MemoryRetrievalCandidate:
    lexical_score = row.get("lexical_score")
    semantic_score = row.get("semantic_score")
    return MemoryRetrievalCandidate(
        record=_row_to_memory_record(row),
        lexical_score=float(lexical_score) if isinstance(lexical_score, int | float) else None,
        semantic_score=float(semantic_score) if isinstance(semantic_score, int | float) else None,
    )
