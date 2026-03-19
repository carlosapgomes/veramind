"""Application-layer request and response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Sequence

from .ports import ExecutionRecord, KnowledgeRecord, MemoryRecord


@dataclass(frozen=True, slots=True)
class SaveMemoryRequest:
    """Application request for durable memory persistence."""

    text: str
    type: str
    scope: str
    source: str
    salience: float | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchMemoryRequest:
    """Application request for memory retrieval."""

    text: str
    limit: int = 10
    min_salience: float | None = None
    query_embedding: tuple[float, ...] | None = None


@dataclass(frozen=True, slots=True)
class CaptureKnowledgeRequest:
    """Application request for durable knowledge capture."""

    title: str
    text: str
    kind: str
    source: str
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchKnowledgeRequest:
    """Application request for knowledge retrieval."""

    text: str
    limit: int = 10
    related_to: str | None = None


@dataclass(frozen=True, slots=True)
class LinkKnowledgeItemsRequest:
    """Application request for explicit semantic relationships."""

    left_id: str
    right_id: str
    relation: str
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SaveExecutionRequest:
    """Application request for workflow-neutral execution persistence."""

    title: str
    kind: str
    state: str
    source: str
    project_id: str | None = None
    due_at: datetime | None = None
    review_at: datetime | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchExecutionRequest:
    """Application request for execution retrieval."""

    limit: int = 50
    states: tuple[str, ...] = ()
    project_id: str | None = None
    due_before: datetime | None = None
    review_before: datetime | None = None


@dataclass(frozen=True, slots=True)
class ContextBundleRequest:
    """Application request for a bounded cross-domain context bundle."""

    query: str
    memory_limit: int = 5
    knowledge_limit: int = 5
    execution_limit: int = 5


@dataclass(frozen=True, slots=True)
class ReviewQueueRequest:
    """Application request for review-oriented execution retrieval."""

    reference_at: datetime
    limit: int = 20


@dataclass(frozen=True, slots=True)
class ContextBundle:
    """Grouped cross-domain context for agent use."""

    memories: Sequence[MemoryRecord] = ()
    knowledge: Sequence[KnowledgeRecord] = ()
    execution: Sequence[ExecutionRecord] = ()
