from __future__ import annotations

from datetime import UTC, datetime

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


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


class FakeMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self.record = MemoryRecord(
            id="mem-1",
            text="User prefers concise answers.",
            type="preference",
            scope="long",
            salience=0.9,
            created_at=_now(),
            updated_at=_now(),
            last_used_at=None,
            source="manual",
        )

    def get(self, record_id: str) -> MemoryRecord | None:
        return self.record if record_id == self.record.id else None

    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        self.record = record
        return record

    def find_similar(self, *, text: str, limit: int = 5) -> list[MemoryRecord]:
        if text and limit > 0:
            return [self.record]
        return []

    def search(self, query: MemorySearchQuery) -> list[MemoryRecord]:
        if query.limit > 0:
            return [self.record]
        return []


class FakeKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self.record = KnowledgeRecord(
            id="note-1",
            title="Hermes note",
            text="Hermes provides MCP support.",
            kind="reference",
            created_at=_now(),
            updated_at=_now(),
            source="manual",
        )
        self.link = KnowledgeLinkRecord(
            id="link-1",
            left_id="note-1",
            right_id="note-2",
            relation="supports",
            created_at=_now(),
        )

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self.record if record_id == self.record.id else None

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self.record = record
        return record

    def search(self, query: KnowledgeSearchQuery) -> list[KnowledgeRecord]:
        if query.limit > 0:
            return [self.record]
        return []

    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        self.link = link
        return link

    def list_links(self, record_id: str) -> list[KnowledgeLinkRecord]:
        if record_id == self.record.id:
            return [self.link]
        return []


class FakeExecutionRepository(ExecutionRepository):
    def __init__(self) -> None:
        self.record = ExecutionRecord(
            id="task-1",
            title="Define repository ports",
            kind="task",
            state="next",
            created_at=_now(),
            updated_at=_now(),
            source="manual",
            review_at=_now(),
        )

    def get(self, record_id: str) -> ExecutionRecord | None:
        return self.record if record_id == self.record.id else None

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        self.record = record
        return record

    def search(self, query: ExecutionQuery) -> list[ExecutionRecord]:
        if query.limit > 0:
            return [self.record]
        return []

    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> list[ExecutionRecord]:
        if limit > 0 and self.record.review_at and self.record.review_at <= reference_at:
            return [self.record]
        return []


class FakeUnitOfWork(PersistenceUnitOfWork):
    def __init__(self) -> None:
        self._memories = FakeMemoryRepository()
        self._knowledge = FakeKnowledgeRepository()
        self._execution = FakeExecutionRepository()
        self.committed = False
        self.rolled_back = False

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
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_memory_record_keeps_the_memory_foundation_fields() -> None:
    record = FakeMemoryRepository().get("mem-1")

    assert record is not None
    assert record.type == "preference"
    assert record.scope == "long"
    assert record.embedding is None
    assert record.metadata == {}


def test_knowledge_repository_exposes_records_and_links() -> None:
    repository = FakeKnowledgeRepository()

    records = repository.search(KnowledgeSearchQuery(text="Hermes"))
    links = repository.list_links("note-1")

    assert records[0].kind == "reference"
    assert links[0].relation == "supports"


def test_execution_repository_is_workflow_neutral_and_review_aware() -> None:
    repository = FakeExecutionRepository()

    records = repository.search(ExecutionQuery(states=("next",)))
    due = repository.list_due_for_review(reference_at=_now())

    assert records[0].kind == "task"
    assert due[0].state == "next"


def test_unit_of_work_coordinates_the_three_repository_ports() -> None:
    unit_of_work = FakeUnitOfWork()

    assert unit_of_work.memories.get("mem-1") is not None
    assert unit_of_work.knowledge.get("note-1") is not None
    assert unit_of_work.execution.get("task-1") is not None

    unit_of_work.commit()
    unit_of_work.rollback()

    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is True
