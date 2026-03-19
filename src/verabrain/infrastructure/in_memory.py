"""In-memory infrastructure adapters for repository and unit-of-work ports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterable, Sequence

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


@dataclass(slots=True)
class InMemoryPersistenceStore:
    """Committed in-memory state shared across unit-of-work instances."""

    memories: dict[str, MemoryRecord] = field(default_factory=dict)
    knowledge: dict[str, KnowledgeRecord] = field(default_factory=dict)
    knowledge_links: dict[str, KnowledgeLinkRecord] = field(default_factory=dict)
    execution: dict[str, ExecutionRecord] = field(default_factory=dict)


class InMemoryMemoryRepository(MemoryRepository):
    """In-memory repository for durable memory records."""

    def __init__(self, workspace_getter: Callable[[], InMemoryPersistenceStore]) -> None:
        self._workspace_getter = workspace_getter

    def get(self, record_id: str) -> MemoryRecord | None:
        return self._workspace_getter().memories.get(record_id)

    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        self._workspace_getter().memories[record.id] = record
        return record

    def find_similar(self, *, text: str, limit: int = 5) -> Sequence[MemoryRecord]:
        return _rank_memories(
            records=self._workspace_getter().memories.values(),
            text=text,
            limit=limit,
            min_salience=None,
        )

    def search(self, query: MemorySearchQuery) -> Sequence[MemoryRecord]:
        return _rank_memories(
            records=self._workspace_getter().memories.values(),
            text=query.text,
            limit=query.limit,
            min_salience=query.min_salience,
        )


class InMemoryKnowledgeRepository(KnowledgeRepository):
    """In-memory repository for knowledge records and explicit links."""

    def __init__(self, workspace_getter: Callable[[], InMemoryPersistenceStore]) -> None:
        self._workspace_getter = workspace_getter

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self._workspace_getter().knowledge.get(record_id)

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self._workspace_getter().knowledge[record.id] = record
        return record

    def search(self, query: KnowledgeSearchQuery) -> Sequence[KnowledgeRecord]:
        workspace = self._workspace_getter()
        related_ids = _related_knowledge_ids(
            links=workspace.knowledge_links.values(),
            related_to=query.related_to,
        )
        ranked: list[tuple[int, float, str, KnowledgeRecord]] = []
        for record in workspace.knowledge.values():
            if related_ids is not None and record.id not in related_ids:
                continue
            haystack = f"{record.title} {record.text}"
            score = _text_score(query.text, haystack)
            if score == 0:
                continue
            ranked.append((score, record.updated_at.timestamp(), record.id, record))
        ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
        return [record for _, _, _, record in ranked[: query.limit]]

    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        self._workspace_getter().knowledge_links[link.id] = link
        return link

    def list_links(self, record_id: str) -> Sequence[KnowledgeLinkRecord]:
        links = [
            link
            for link in self._workspace_getter().knowledge_links.values()
            if link.left_id == record_id or link.right_id == record_id
        ]
        links.sort(key=lambda link: (-link.created_at.timestamp(), link.id))
        return links


class InMemoryExecutionRepository(ExecutionRepository):
    """In-memory repository for workflow-neutral execution records."""

    def __init__(self, workspace_getter: Callable[[], InMemoryPersistenceStore]) -> None:
        self._workspace_getter = workspace_getter

    def get(self, record_id: str) -> ExecutionRecord | None:
        return self._workspace_getter().execution.get(record_id)

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        self._workspace_getter().execution[record.id] = record
        return record

    def search(self, query: ExecutionQuery) -> Sequence[ExecutionRecord]:
        records = [
            record
            for record in self._workspace_getter().execution.values()
            if _matches_execution_query(record, query)
        ]
        records.sort(
            key=lambda record: (
                record.due_at.timestamp() if record.due_at else float("inf"),
                record.review_at.timestamp() if record.review_at else float("inf"),
                -record.updated_at.timestamp(),
                record.id,
            )
        )
        return records[: query.limit]

    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> Sequence[ExecutionRecord]:
        records = [
            record
            for record in self._workspace_getter().execution.values()
            if record.review_at is not None and record.review_at <= reference_at
        ]
        records.sort(
            key=lambda record: (
                record.review_at.timestamp() if record.review_at else float("inf"),
                -record.updated_at.timestamp(),
                record.id,
            )
        )
        return records[:limit]


class InMemoryUnitOfWork(PersistenceUnitOfWork):
    """In-memory unit of work with explicit commit and rollback behavior."""

    def __init__(self, *, store: InMemoryPersistenceStore | None = None) -> None:
        self._store = store or InMemoryPersistenceStore()
        self._workspace = _clone_store(self._store)
        self._memories = InMemoryMemoryRepository(self._current_workspace)
        self._knowledge = InMemoryKnowledgeRepository(self._current_workspace)
        self._execution = InMemoryExecutionRepository(self._current_workspace)

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
        _copy_store(source=self._workspace, destination=self._store)
        self._workspace = _clone_store(self._store)

    def rollback(self) -> None:
        self._workspace = _clone_store(self._store)

    def _current_workspace(self) -> InMemoryPersistenceStore:
        return self._workspace


def _rank_memories(
    *,
    records: Iterable[MemoryRecord],
    text: str,
    limit: int,
    min_salience: float | None,
) -> list[MemoryRecord]:
    ranked: list[tuple[int, float, float, str, MemoryRecord]] = []
    for record in records:
        if min_salience is not None and record.salience < min_salience:
            continue
        score = _text_score(text, record.text)
        if score == 0:
            continue
        ranked.append(
            (
                score,
                record.salience,
                record.updated_at.timestamp(),
                record.id,
                record,
            )
        )
    ranked.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3]))
    return [record for _, _, _, _, record in ranked[:limit]]


def _related_knowledge_ids(
    *,
    links: Iterable[KnowledgeLinkRecord],
    related_to: str | None,
) -> set[str] | None:
    if related_to is None:
        return None
    related_ids: set[str] = set()
    for link in links:
        if link.left_id == related_to:
            related_ids.add(link.right_id)
        if link.right_id == related_to:
            related_ids.add(link.left_id)
    return related_ids


def _matches_execution_query(record: ExecutionRecord, query: ExecutionQuery) -> bool:
    if query.states and record.state not in query.states:
        return False
    if query.project_id is not None and record.project_id != query.project_id:
        return False
    if query.due_before is not None:
        if record.due_at is None or record.due_at > query.due_before:
            return False
    if query.review_before is not None:
        if record.review_at is None or record.review_at > query.review_before:
            return False
    return True


def _text_score(query: str, candidate: str) -> int:
    normalized_query = _normalize_text(query)
    normalized_candidate = _normalize_text(candidate)
    if not normalized_query or not normalized_candidate:
        return 0

    candidate_tokens = set(normalized_candidate.split())
    score = 0
    if normalized_query in normalized_candidate:
        score += 2
    for token in normalized_query.split():
        if token in candidate_tokens:
            score += 1
    return score


def _normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _clone_store(store: InMemoryPersistenceStore) -> InMemoryPersistenceStore:
    return InMemoryPersistenceStore(
        memories=dict(store.memories),
        knowledge=dict(store.knowledge),
        knowledge_links=dict(store.knowledge_links),
        execution=dict(store.execution),
    )


def _copy_store(
    *, source: InMemoryPersistenceStore, destination: InMemoryPersistenceStore
) -> None:
    destination.memories = dict(source.memories)
    destination.knowledge = dict(source.knowledge)
    destination.knowledge_links = dict(source.knowledge_links)
    destination.execution = dict(source.execution)
