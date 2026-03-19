from __future__ import annotations

from datetime import UTC, datetime
from typing import Mapping, Sequence

from verabrain.application import (
    ExecutionQuery,
    ExecutionRecord,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeSearchQuery,
    MemoryRecord,
    MemorySearchQuery,
)
from verabrain.infrastructure import (
    PostgresExecutionRepository,
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresUnitOfWork,
)


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


class FakeCursor:
    def __init__(self, connection: FakeConnection) -> None:
        self._connection = connection

    def execute(self, query: str, params: Mapping[str, object] | None = None) -> None:
        self._connection.executed.append((query, params))

    def fetchone(self) -> Mapping[str, object] | None:
        if not self._connection.one_results:
            return None
        return self._connection.one_results.pop(0)

    def fetchall(self) -> Sequence[Mapping[str, object]]:
        if not self._connection.all_results:
            return []
        return self._connection.all_results.pop(0)

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
    def __init__(
        self,
        *,
        one_results: Sequence[Mapping[str, object] | None] = (),
        all_results: Sequence[Sequence[Mapping[str, object]]] = (),
    ) -> None:
        self.one_results = list(one_results)
        self.all_results = list(all_results)
        self.executed: list[tuple[str, Mapping[str, object] | None]] = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_postgres_memory_repository_upserts_and_maps_memory_rows() -> None:
    connection = FakeConnection(
        one_results=[
            {
                "id": "mem-1",
                "text": "User prefers concise answers.",
                "type": "preference",
                "scope": "long",
                "salience": 0.9,
                "created_at": _now(),
                "updated_at": _now(),
                "last_used_at": None,
                "source": "manual",
                "embedding": [0.1, 0.2],
                "metadata": {"origin": "test"},
            }
        ]
    )
    repository = PostgresMemoryRepository(connection)
    record = MemoryRecord(
        id="mem-1",
        text="User prefers concise answers.",
        type="preference",
        scope="long",
        salience=0.9,
        created_at=_now(),
        updated_at=_now(),
        last_used_at=None,
        source="manual",
        embedding=(0.1, 0.2),
        metadata={"origin": "test"},
    )

    saved = repository.upsert(record)
    loaded = repository.get("mem-1")

    assert saved == record
    query, params = connection.executed[0]
    assert "INSERT INTO memories" in query
    assert "ON CONFLICT (id) DO UPDATE" in query
    assert params is not None
    assert params["embedding"] == [0.1, 0.2]
    assert loaded is not None
    assert loaded.embedding == (0.1, 0.2)
    assert loaded.metadata == {"origin": "test"}


def test_postgres_memory_repository_builds_bounded_search_queries() -> None:
    connection = FakeConnection(
        all_results=[
            [
                {
                    "id": "mem-1",
                    "text": "Project context for Hermes.",
                    "type": "project",
                    "scope": "medium",
                    "salience": 0.8,
                    "created_at": _now(),
                    "updated_at": _now(),
                    "last_used_at": None,
                    "source": "manual",
                    "embedding": None,
                    "metadata": {},
                    "lexical_score": 1.0,
                    "semantic_score": None,
                }
            ],
            [],
        ]
    )
    repository = PostgresMemoryRepository(connection)

    results = repository.search(
        MemorySearchQuery(
            text="Hermes",
            limit=5,
            min_salience=0.6,
            query_embedding=(0.4, 0.5),
        )
    )
    repository.find_similar(text="Project", limit=2)

    search_query, search_params = connection.executed[0]
    similar_query, similar_params = connection.executed[1]
    assert "semantic_score" in search_query
    assert "LIMIT %(candidate_limit)s" in search_query
    assert search_params is not None
    assert search_params["pattern"] == "%Hermes%"
    assert search_params["candidate_limit"] == 20
    assert search_params["query_embedding"] == [0.4, 0.5]
    assert "embedding <=> %(query_embedding)s" in search_query
    assert "LIMIT %(candidate_limit)s" in similar_query
    assert similar_params is not None
    assert similar_params["pattern"] == "%Project%"
    assert similar_params["candidate_limit"] == 10
    assert results[0].id == "mem-1"


def test_postgres_memory_repository_uses_lexical_only_query_when_semantic_input_is_missing() -> None:
    connection = FakeConnection(
        all_results=[
            [
                {
                    "id": "mem-1",
                    "text": "Hermes lexical context",
                    "type": "project",
                    "scope": "medium",
                    "salience": 0.8,
                    "created_at": _now(),
                    "updated_at": _now(),
                    "last_used_at": None,
                    "source": "manual",
                    "embedding": None,
                    "metadata": {},
                    "lexical_score": 1.0,
                    "semantic_score": None,
                }
            ]
        ]
    )
    repository = PostgresMemoryRepository(connection)

    results = repository.search(MemorySearchQuery(text="Hermes", limit=2))

    search_query, search_params = connection.executed[0]
    assert "NULL AS semantic_score" in search_query
    assert "embedding <=> %(query_embedding)s" not in search_query
    assert search_params is not None
    assert "query_embedding" not in search_params
    assert search_params["candidate_limit"] == 10
    assert results[0].id == "mem-1"


def test_postgres_memory_repository_reranks_candidates_with_hybrid_signals() -> None:
    connection = FakeConnection(
        all_results=[
            [
                {
                    "id": "mem-lexical",
                    "text": "Hermes runtime notes.",
                    "type": "preference",
                    "scope": "long",
                    "salience": 0.8,
                    "created_at": _now(),
                    "updated_at": datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
                    "last_used_at": None,
                    "source": "manual",
                    "embedding": [0.1, 0.2],
                    "metadata": {},
                    "lexical_score": 1.0,
                    "semantic_score": 0.2,
                },
                {
                    "id": "mem-semantic",
                    "text": "Long-term runtime shell context.",
                    "type": "decision",
                    "scope": "long",
                    "salience": 0.7,
                    "created_at": _now(),
                    "updated_at": _now(),
                    "last_used_at": _now(),
                    "source": "manual",
                    "embedding": [0.2, 0.3],
                    "metadata": {},
                    "lexical_score": 0.0,
                    "semantic_score": 0.9,
                },
            ]
        ]
    )
    repository = PostgresMemoryRepository(connection)

    results = repository.search(
        MemorySearchQuery(text="Hermes runtime", limit=1, query_embedding=(0.2, 0.3))
    )

    assert [record.id for record in results] == ["mem-semantic"]


def test_postgres_knowledge_repository_saves_searches_and_lists_links() -> None:
    connection = FakeConnection(
        all_results=[
            [
                {
                    "id": "note-2",
                    "title": "MCP integration",
                    "text": "Hermes connects through stdio.",
                    "kind": "note",
                    "created_at": _now(),
                    "updated_at": _now(),
                    "source": "manual",
                    "metadata": {"topic": "mcp"},
                }
            ],
            [
                {
                    "id": "link-1",
                    "left_id": "note-1",
                    "right_id": "note-2",
                    "relation": "supports",
                    "created_at": _now(),
                    "metadata": {},
                }
            ],
        ]
    )
    repository = PostgresKnowledgeRepository(connection)

    repository.save(
        KnowledgeRecord(
            id="note-1",
            title="Hermes overview",
            text="Hermes is the runtime shell.",
            kind="reference",
            created_at=_now(),
            updated_at=_now(),
            source="manual",
            metadata={"topic": "runtime"},
        )
    )
    repository.save_link(
        KnowledgeLinkRecord(
            id="link-1",
            left_id="note-1",
            right_id="note-2",
            relation="supports",
            created_at=_now(),
        )
    )
    results = repository.search(
        KnowledgeSearchQuery(text="Hermes", limit=3, related_to="note-1")
    )
    links = repository.list_links("note-1")

    search_query, search_params = connection.executed[2]
    assert "FROM knowledge_items" in search_query
    assert "EXISTS (" in search_query
    assert search_params is not None
    assert search_params["related_to"] == "note-1"
    assert results[0].id == "note-2"
    assert links[0].relation == "supports"


def test_postgres_execution_repository_filters_and_lists_review_queue() -> None:
    connection = FakeConnection(
        all_results=[
            [
                {
                    "id": "task-1",
                    "title": "Ship adapter",
                    "kind": "task",
                    "state": "next",
                    "created_at": _now(),
                    "updated_at": _now(),
                    "source": "manual",
                    "project_id": "proj-1",
                    "due_at": datetime(2026, 3, 20, 12, 0, tzinfo=UTC),
                    "review_at": datetime(2026, 3, 19, 11, 0, tzinfo=UTC),
                    "metadata": {},
                }
            ],
            [
                {
                    "id": "task-2",
                    "title": "Review links",
                    "kind": "review",
                    "state": "waiting",
                    "created_at": _now(),
                    "updated_at": _now(),
                    "source": "manual",
                    "project_id": "proj-2",
                    "due_at": datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
                    "review_at": datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
                    "metadata": {},
                }
            ],
        ]
    )
    repository = PostgresExecutionRepository(connection)
    repository.save(
        ExecutionRecord(
            id="task-1",
            title="Ship adapter",
            kind="task",
            state="next",
            created_at=_now(),
            updated_at=_now(),
            source="manual",
            project_id="proj-1",
            due_at=datetime(2026, 3, 20, 12, 0, tzinfo=UTC),
            review_at=datetime(2026, 3, 19, 11, 0, tzinfo=UTC),
        )
    )

    search_results = repository.search(
        ExecutionQuery(
            limit=5,
            states=("next", "waiting"),
            project_id="proj-1",
            due_before=datetime(2026, 3, 21, 12, 0, tzinfo=UTC),
            review_before=datetime(2026, 3, 19, 12, 0, tzinfo=UTC),
        )
    )
    review_results = repository.list_due_for_review(reference_at=_now(), limit=5)

    search_query, search_params = connection.executed[1]
    review_query, review_params = connection.executed[2]
    assert "state = ANY(%(states)s)" in search_query
    assert "project_id = %(project_id)s" in search_query
    assert search_params is not None
    assert search_params["states"] == ["next", "waiting"]
    assert search_results[0].id == "task-1"
    assert "review_at <= %(reference_at)s" in review_query
    assert review_params is not None
    assert review_params["limit"] == 5
    assert review_results[0].id == "task-2"


def test_postgres_unit_of_work_delegates_commit_and_rollback() -> None:
    connection = FakeConnection()
    unit_of_work = PostgresUnitOfWork(connection_factory=lambda: connection)

    unit_of_work.commit()
    unit_of_work.rollback()

    assert connection.commits == 1
    assert connection.rollbacks == 1
    assert isinstance(unit_of_work.memories, PostgresMemoryRepository)
    assert isinstance(unit_of_work.knowledge, PostgresKnowledgeRepository)
    assert isinstance(unit_of_work.execution, PostgresExecutionRepository)
