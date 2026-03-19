"""Application-layer repository and persistence ports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """Durable user-context record for the memory layer."""

    id: str
    text: str
    type: str
    scope: str
    salience: float
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None
    source: str
    embedding: tuple[float, ...] | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MemorySearchQuery:
    """Query object for bounded memory retrieval."""

    text: str
    limit: int = 10
    min_salience: float | None = None
    query_embedding: tuple[float, ...] | None = None


@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    """Durable knowledge item for notes, captures, and references."""

    id: str
    title: str
    text: str
    kind: str
    created_at: datetime
    updated_at: datetime
    source: str
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KnowledgeLinkRecord:
    """Explicit semantic relationship between two knowledge items."""

    id: str
    left_id: str
    right_id: str
    relation: str
    created_at: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KnowledgeSearchQuery:
    """Query object for knowledge retrieval."""

    text: str
    limit: int = 10
    related_to: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    """Workflow-neutral execution record for tasks and reviews."""

    id: str
    title: str
    kind: str
    state: str
    created_at: datetime
    updated_at: datetime
    source: str
    project_id: str | None = None
    due_at: datetime | None = None
    review_at: datetime | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionQuery:
    """Filter object for execution retrieval."""

    limit: int = 50
    states: tuple[str, ...] = ()
    project_id: str | None = None
    due_before: datetime | None = None
    review_before: datetime | None = None


class MemoryRepository(ABC):
    """Persistence port for memory-layer records."""

    @abstractmethod
    def get(self, record_id: str) -> MemoryRecord | None:
        """Load a memory record by identifier."""

    @abstractmethod
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        """Create or update a memory record."""

    @abstractmethod
    def find_similar(self, *, text: str, limit: int = 5) -> Sequence[MemoryRecord]:
        """Return candidate duplicate memories for a text fragment."""

    @abstractmethod
    def search(self, query: MemorySearchQuery) -> Sequence[MemoryRecord]:
        """Search memories for bounded retrieval."""


class KnowledgeRepository(ABC):
    """Persistence port for knowledge records and semantic links."""

    @abstractmethod
    def get(self, record_id: str) -> KnowledgeRecord | None:
        """Load a knowledge record by identifier."""

    @abstractmethod
    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        """Create or update a knowledge record."""

    @abstractmethod
    def search(self, query: KnowledgeSearchQuery) -> Sequence[KnowledgeRecord]:
        """Search knowledge records."""

    @abstractmethod
    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        """Create or update a semantic link."""

    @abstractmethod
    def list_links(self, record_id: str) -> Sequence[KnowledgeLinkRecord]:
        """List semantic links related to a knowledge record."""


class ExecutionRepository(ABC):
    """Persistence port for workflow-neutral execution records."""

    @abstractmethod
    def get(self, record_id: str) -> ExecutionRecord | None:
        """Load an execution record by identifier."""

    @abstractmethod
    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        """Create or update an execution record."""

    @abstractmethod
    def search(self, query: ExecutionQuery) -> Sequence[ExecutionRecord]:
        """Search execution records by filter criteria."""

    @abstractmethod
    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> Sequence[ExecutionRecord]:
        """List execution records that should be reviewed."""


class PersistenceUnitOfWork(ABC):
    """Coordinate multi-repository persistence flows."""

    @property
    @abstractmethod
    def memories(self) -> MemoryRepository:
        """Expose the memory repository."""

    @property
    @abstractmethod
    def knowledge(self) -> KnowledgeRepository:
        """Expose the knowledge repository."""

    @property
    @abstractmethod
    def execution(self) -> ExecutionRepository:
        """Expose the execution repository."""

    @abstractmethod
    def commit(self) -> None:
        """Persist the current unit of work."""

    @abstractmethod
    def rollback(self) -> None:
        """Discard the current unit of work."""
