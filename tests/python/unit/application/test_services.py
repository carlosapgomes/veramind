from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence, cast

import pytest

from verabrain.application import (
    CaptureKnowledgeRequest,
    ContextBundleRequest,
    ExecutionApplicationService,
    ExecutionQuery,
    ExecutionRecord,
    ExecutionRepository,
    KnowledgeApplicationService,
    LinkKnowledgeItemsRequest,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeRepository,
    MemoryApplicationService,
    MemoryRecord,
    MemoryRepository,
    PersistenceUnitOfWork,
    ReviewQueueRequest,
    SaveExecutionRequest,
    SaveMemoryRequest,
    SearchExecutionRequest,
    SearchKnowledgeRequest,
    SearchMemoryRequest,
    VeraBrainApplication,
)


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


class RecordingMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self.saved: MemoryRecord | None = None
        self.last_find_similar_text: str | None = None
        self.last_find_similar_limit: int | None = None
        self.last_search_query = None
        self.result = [
            MemoryRecord(
                id="mem-existing",
                text="User prefers concise answers.",
                type="preference",
                scope="long",
                salience=0.9,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            )
        ]
        self.similar_result: Sequence[MemoryRecord] = ()

    def get(self, record_id: str) -> MemoryRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        self.saved = record
        return record

    def find_similar(self, *, text: str, limit: int = 5) -> Sequence[MemoryRecord]:
        self.last_find_similar_text = text
        self.last_find_similar_limit = limit
        return self.similar_result[:limit]

    def search(self, query):  # type: ignore[no-untyped-def]
        self.last_search_query = query
        return self.result[: query.limit]


class RecordingKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self.saved: KnowledgeRecord | None = None
        self.saved_link: KnowledgeLinkRecord | None = None
        self.last_search_query = None
        self.result = [
            KnowledgeRecord(
                id="note-existing",
                title="Hermes note",
                text="Hermes supports MCP.",
                kind="reference",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            )
        ]

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self.saved = record
        return record

    def search(self, query):  # type: ignore[no-untyped-def]
        self.last_search_query = query
        return self.result[: query.limit]

    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        self.saved_link = link
        return link

    def list_links(self, record_id: str) -> Sequence[KnowledgeLinkRecord]:
        return [self.saved_link] if self.saved_link and record_id == self.saved_link.left_id else []


class RecordingExecutionRepository(ExecutionRepository):
    def __init__(self) -> None:
        self.saved: ExecutionRecord | None = None
        self.last_search_query: ExecutionQuery | None = None
        self.last_review_reference: datetime | None = None
        self.last_review_limit: int | None = None
        self.result = [
            ExecutionRecord(
                id="task-existing",
                title="Define services",
                kind="task",
                state="next",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
                review_at=_now(),
            )
        ]

    def get(self, record_id: str) -> ExecutionRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        self.saved = record
        return record

    def search(self, query: ExecutionQuery) -> Sequence[ExecutionRecord]:
        self.last_search_query = query
        return self.result[: query.limit]

    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> Sequence[ExecutionRecord]:
        self.last_review_reference = reference_at
        self.last_review_limit = limit
        return self.result[:limit]


class RecordingUnitOfWork(PersistenceUnitOfWork):
    def __init__(self) -> None:
        self._memories = RecordingMemoryRepository()
        self._knowledge = RecordingKnowledgeRepository()
        self._execution = RecordingExecutionRepository()
        self.commits = 0
        self.rollbacks = 0

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
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class FailingMemoryRepository(RecordingMemoryRepository):
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        raise RuntimeError("boom")


class FailingUnitOfWork(RecordingUnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self._memories = FailingMemoryRepository()


def test_memory_service_saves_records_and_commits() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    service = MemoryApplicationService(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "mem-1",
    )

    record = service.save(
        SaveMemoryRequest(
            text="User prefers concise answers.",
            type="preference",
            scope="long",
            source="manual",
            salience=0.8,
        )
    )

    assert record.id == "mem-1"
    assert record.created_at == _now()
    assert memory_repository.last_find_similar_text == "User prefers concise answers."
    assert memory_repository.last_find_similar_limit == 5
    assert unit_of_work.commits == 1
    assert unit_of_work.rollbacks == 0


def test_memory_service_exposes_write_classification_for_memory_candidates() -> None:
    unit_of_work = RecordingUnitOfWork()
    service = MemoryApplicationService(unit_of_work=unit_of_work, clock=_now)

    result = service.classify_write(
        SaveMemoryRequest(
            text="User prefers concise answers.",
            type="preference",
            scope="long",
            source="manual",
        )
    )

    assert result.disposition == "memory_candidate"
    assert result.reason == "durable_signal"
    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 0


def test_memory_service_exposes_write_classification_for_ignored_inputs() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    service = MemoryApplicationService(unit_of_work=unit_of_work, clock=_now)

    result = service.classify_write(
        SaveMemoryRequest(
            text="thanks",
            type="profile",
            scope="short",
            source="manual",
        )
    )

    assert result.disposition == "ignore"
    assert result.reason == "transient_message"
    assert memory_repository.saved is None
    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 0


def test_memory_service_updates_existing_memory_when_duplicate_is_materially_the_same() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    existing = MemoryRecord(
        id="mem-existing",
        text="User prefers concise answers.",
        type="preference",
        scope="long",
        salience=0.9,
        created_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
        last_used_at=datetime(2026, 3, 18, 15, 0, tzinfo=UTC),
        source="manual",
        embedding=(0.1, 0.2),
        metadata={"origin": "existing", "keep": True},
    )
    memory_repository.similar_result = (existing,)
    service = MemoryApplicationService(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "mem-new",
    )

    saved = service.save(
        SaveMemoryRequest(
            text="User prefers concise answers!",
            type="preference",
            scope="long",
            source="import",
            metadata={"origin": "updated"},
        )
    )

    assert saved.id == "mem-existing"
    assert saved.created_at == existing.created_at
    assert saved.updated_at == _now()
    assert saved.last_used_at == existing.last_used_at
    assert saved.embedding == (0.1, 0.2)
    assert saved.salience == 0.9
    assert saved.metadata == {"origin": "updated", "keep": True}
    assert memory_repository.saved == saved
    assert unit_of_work.commits == 1


def test_memory_service_creates_new_memory_when_similar_candidates_are_not_material_duplicates() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    memory_repository.similar_result = (
        MemoryRecord(
            id="mem-existing",
            text="User likes detailed weekend plans.",
            type="habit",
            scope="medium",
            salience=0.4,
            created_at=_now(),
            updated_at=_now(),
            last_used_at=None,
            source="manual",
        ),
    )
    service = MemoryApplicationService(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "mem-2",
    )

    saved = service.save(
        SaveMemoryRequest(
            text="Project timeline depends on Hermes MCP delivery.",
            type="project",
            scope="medium",
            source="manual",
        )
    )

    assert saved.id == "mem-2"
    assert saved.created_at == _now()
    assert memory_repository.saved == saved
    assert unit_of_work.commits == 1


def test_memory_service_rolls_back_when_write_fails() -> None:
    unit_of_work = FailingUnitOfWork()
    service = MemoryApplicationService(unit_of_work=unit_of_work, clock=_now)

    with pytest.raises(RuntimeError, match="boom"):
        service.save(
            SaveMemoryRequest(
                text="Failure case",
                type="profile",
                scope="short",
                source="manual",
            )
        )

    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1


def test_memory_service_passes_optional_query_embedding_through_the_port() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    service = MemoryApplicationService(unit_of_work=unit_of_work, clock=_now)

    service.search(
        SearchMemoryRequest(
            text="Hermes",
            limit=3,
            min_salience=0.5,
            query_embedding=(0.1, 0.2, 0.3),
        )
    )

    assert memory_repository.last_search_query is not None
    assert memory_repository.last_search_query.query_embedding == (0.1, 0.2, 0.3)


def test_knowledge_service_captures_links_and_searches() -> None:
    unit_of_work = RecordingUnitOfWork()
    service = KnowledgeApplicationService(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "note-1",
    )

    captured = service.capture(
        CaptureKnowledgeRequest(
            title="Hermes note",
            text="Hermes supports MCP.",
            kind="reference",
            source="manual",
        )
    )
    linked = service.link(
        LinkKnowledgeItemsRequest(
            left_id="note-1",
            right_id="note-2",
            relation="supports",
        )
    )
    results = service.search(SearchKnowledgeRequest(text="Hermes", limit=1))

    assert captured.id == "note-1"
    assert linked.id == "note-1"
    assert results[0].kind == "reference"
    assert unit_of_work.commits == 2


def test_execution_service_searches_and_lists_review_queue() -> None:
    unit_of_work = RecordingUnitOfWork()
    execution_repository = cast(RecordingExecutionRepository, unit_of_work.execution)
    service = ExecutionApplicationService(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "task-1",
    )

    saved = service.save(
        SaveExecutionRequest(
            title="Define services",
            kind="task",
            state="next",
            source="manual",
            review_at=_now(),
        )
    )
    results = service.search(SearchExecutionRequest(limit=1, states=("next",)))
    review = service.list_review_queue(ReviewQueueRequest(reference_at=_now(), limit=1))

    assert saved.id == "task-1"
    assert execution_repository.last_search_query is not None
    assert execution_repository.last_search_query.states == ("next",)
    assert review[0].state == "next"
    assert results[0].kind == "task"


def test_facade_builds_a_bounded_cross_domain_context_bundle() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    execution_repository = cast(RecordingExecutionRepository, unit_of_work.execution)
    application = VeraBrainApplication(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "fixed-id",
    )

    bundle = application.context.get_bundle(
        ContextBundleRequest(
            query="Hermes",
            memory_limit=1,
            knowledge_limit=1,
            execution_limit=1,
        )
    )

    assert bundle.memories[0].type == "preference"
    assert bundle.knowledge[0].kind == "reference"
    assert bundle.execution[0].state == "next"
    assert memory_repository.last_search_query is not None
    assert memory_repository.last_search_query.text == "Hermes"
    assert memory_repository.last_search_query.query_embedding is None
    assert execution_repository.last_search_query is not None
    assert execution_repository.last_search_query.limit == 1


def test_context_bundle_uses_optional_memory_query_embedding_provider() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    application = VeraBrainApplication(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "fixed-id",
        memory_query_embedding_provider=lambda query: (
            (0.9, 0.1) if query == "Hermes" else None
        ),
    )

    bundle = application.context.get_bundle(
        ContextBundleRequest(
            query="Hermes",
            memory_limit=1,
            knowledge_limit=1,
            execution_limit=1,
        )
    )

    assert bundle.memories[0].type == "preference"
    assert memory_repository.last_search_query is not None
    assert memory_repository.last_search_query.limit == 1
    assert memory_repository.last_search_query.query_embedding == (0.9, 0.1)


def test_context_bundle_falls_back_when_memory_query_embedding_provider_fails() -> None:
    unit_of_work = RecordingUnitOfWork()
    memory_repository = cast(RecordingMemoryRepository, unit_of_work.memories)
    application = VeraBrainApplication(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "fixed-id",
        memory_query_embedding_provider=lambda query: (_ for _ in ()).throw(
            RuntimeError("embedding backend unavailable")
        ),
    )

    bundle = application.context.get_bundle(
        ContextBundleRequest(
            query="Hermes",
            memory_limit=1,
            knowledge_limit=1,
            execution_limit=1,
        )
    )

    assert bundle.memories[0].type == "preference"
    assert memory_repository.last_search_query is not None
    assert memory_repository.last_search_query.query_embedding is None
