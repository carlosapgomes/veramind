from __future__ import annotations

from datetime import UTC, datetime

from verabrain.application import (
    ExecutionQuery,
    ExecutionRecord,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeSearchQuery,
    MemoryRecord,
    MemorySearchQuery,
    SaveMemoryRequest,
    VeraBrainApplication,
)
from verabrain.infrastructure import InMemoryPersistenceStore, InMemoryUnitOfWork


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


def test_in_memory_unit_of_work_persists_committed_records_across_scopes() -> None:
    store = InMemoryPersistenceStore()
    application = VeraBrainApplication(
        unit_of_work=InMemoryUnitOfWork(store=store),
        clock=_now,
        id_generator=lambda: "mem-1",
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

    reloaded = InMemoryUnitOfWork(store=store)

    assert reloaded.memories.get(saved.id) == saved


def test_in_memory_unit_of_work_rollback_discards_staged_changes() -> None:
    store = InMemoryPersistenceStore()
    unit_of_work = InMemoryUnitOfWork(store=store)
    staged = MemoryRecord(
        id="mem-staged",
        text="Draft memory",
        type="project",
        scope="short",
        salience=0.5,
        created_at=_now(),
        updated_at=_now(),
        last_used_at=None,
        source="manual",
    )

    unit_of_work.memories.upsert(staged)
    unit_of_work.rollback()

    reloaded = InMemoryUnitOfWork(store=store)
    assert reloaded.memories.get("mem-staged") is None


def test_in_memory_memory_repository_supports_similarity_and_bounded_search() -> None:
    store = InMemoryPersistenceStore(
        memories={
            "mem-1": MemoryRecord(
                id="mem-1",
                text="User prefers concise answers for project updates.",
                type="preference",
                scope="long",
                salience=0.9,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            ),
            "mem-2": MemoryRecord(
                id="mem-2",
                text="Project timeline depends on Hermes MCP delivery.",
                type="project",
                scope="medium",
                salience=0.7,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            ),
            "mem-3": MemoryRecord(
                id="mem-3",
                text="User likes detailed weekend plans.",
                type="habit",
                scope="medium",
                salience=0.2,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            ),
        }
    )
    unit_of_work = InMemoryUnitOfWork(store=store)

    similar = unit_of_work.memories.find_similar(text="concise project answers", limit=2)
    results = unit_of_work.memories.search(
        MemorySearchQuery(text="project", limit=5, min_salience=0.5)
    )

    assert [record.id for record in similar] == ["mem-1", "mem-2"]
    assert [record.id for record in results] == ["mem-1", "mem-2"]


def test_in_memory_knowledge_repository_searches_related_records_and_links() -> None:
    store = InMemoryPersistenceStore(
        knowledge={
            "note-1": KnowledgeRecord(
                id="note-1",
                title="Hermes overview",
                text="Hermes is the runtime shell.",
                kind="reference",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            ),
            "note-2": KnowledgeRecord(
                id="note-2",
                title="MCP integration",
                text="Hermes connects to MCP servers through stdio.",
                kind="note",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            ),
        },
        knowledge_links={
            "link-1": KnowledgeLinkRecord(
                id="link-1",
                left_id="note-1",
                right_id="note-2",
                relation="supports",
                created_at=_now(),
            )
        },
    )
    unit_of_work = InMemoryUnitOfWork(store=store)

    results = unit_of_work.knowledge.search(
        KnowledgeSearchQuery(text="Hermes MCP", limit=5, related_to="note-1")
    )
    links = unit_of_work.knowledge.list_links("note-1")

    assert [record.id for record in results] == ["note-2"]
    assert links[0].relation == "supports"


def test_in_memory_execution_repository_filters_search_and_review_queries() -> None:
    store = InMemoryPersistenceStore(
        execution={
            "task-1": ExecutionRecord(
                id="task-1",
                title="Ship MCP adapter",
                kind="task",
                state="next",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
                project_id="proj-1",
                due_at=datetime(2026, 3, 20, 12, 0, tzinfo=UTC),
                review_at=datetime(2026, 3, 19, 11, 0, tzinfo=UTC),
            ),
            "task-2": ExecutionRecord(
                id="task-2",
                title="Archive old notes",
                kind="task",
                state="done",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
                project_id="proj-1",
                due_at=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
                review_at=datetime(2026, 3, 22, 12, 0, tzinfo=UTC),
            ),
            "task-3": ExecutionRecord(
                id="task-3",
                title="Review knowledge links",
                kind="review",
                state="waiting",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
                project_id="proj-2",
                due_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
                review_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
            ),
        }
    )
    unit_of_work = InMemoryUnitOfWork(store=store)

    search_results = unit_of_work.execution.search(
        ExecutionQuery(
            limit=5,
            states=("next", "waiting"),
            project_id="proj-1",
            due_before=datetime(2026, 3, 21, 12, 0, tzinfo=UTC),
        )
    )
    review_results = unit_of_work.execution.list_due_for_review(
        reference_at=_now(),
        limit=5,
    )

    assert [record.id for record in search_results] == ["task-1"]
    assert [record.id for record in review_results] == ["task-3", "task-1"]
