"""Callable application services built on request contracts and ports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Callable, Sequence
from uuid import uuid4

from .embeddings import MemoryEmbeddingProvider
from .contracts import (
    CaptureKnowledgeRequest,
    ContextBundle,
    ContextBundleRequest,
    LinkKnowledgeItemsRequest,
    ReviewQueueRequest,
    SaveExecutionRequest,
    SaveMemoryRequest,
    SearchExecutionRequest,
    SearchKnowledgeRequest,
    SearchMemoryRequest,
)
from verabrain.core.memory_pipeline import (
    MemoryDuplicateAssessment,
    MemoryWriteClassification,
    assess_memory_duplicate,
    classify_memory_write,
    validate_memory_record_shape,
)
from verabrain.core.retrieval import (
    resolve_query_embedding,
)
from .ports import (
    ExecutionQuery,
    ExecutionRecord,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeSearchQuery,
    MemoryRecord,
    MemorySearchQuery,
    PersistenceUnitOfWork,
)

Clock = Callable[[], datetime]
IdGenerator = Callable[[], str]
QueryEmbeddingProvider = Callable[[str], tuple[float, ...] | None]


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _new_id() -> str:
    return uuid4().hex


@dataclass(slots=True)
class MemoryApplicationService:
    """Application service for memory persistence and retrieval."""

    unit_of_work: PersistenceUnitOfWork
    clock: Clock = _utc_now
    id_generator: IdGenerator = _new_id
    memory_embedding_provider: MemoryEmbeddingProvider | None = None

    def classify_write(self, request: SaveMemoryRequest) -> MemoryWriteClassification:
        """Classify whether a write request belongs in the memory pipeline."""

        return classify_memory_write(request.text)

    def save(self, request: SaveMemoryRequest) -> MemoryRecord:
        self._validate_request(request)
        now = self.clock()
        duplicate = self._assess_duplicate(request)
        record = self._build_memory_record(request, now=now, duplicate=duplicate)
        try:
            saved = self.unit_of_work.memories.upsert(record)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise
        return saved

    def search(self, request: SearchMemoryRequest) -> Sequence[MemoryRecord]:
        return self.unit_of_work.memories.search(
            MemorySearchQuery(
                text=request.text,
                limit=request.limit,
                min_salience=request.min_salience,
                query_embedding=request.query_embedding,
            )
        )

    def _validate_request(self, request: SaveMemoryRequest) -> None:
        validate_memory_record_shape(request.type, request.scope)

    def _assess_duplicate(self, request: SaveMemoryRequest) -> MemoryDuplicateAssessment:
        candidates = self.unit_of_work.memories.find_similar(text=request.text, limit=5)
        return assess_memory_duplicate(request.text, candidates)

    def _build_memory_record(
        self,
        request: SaveMemoryRequest,
        *,
        now: datetime,
        duplicate: MemoryDuplicateAssessment,
    ) -> MemoryRecord:
        matched = duplicate.matched_record
        if matched is None:
            return MemoryRecord(
                id=self.id_generator(),
                text=request.text,
                type=request.type,
                scope=request.scope,
                salience=request.salience if request.salience is not None else 0.5,
                created_at=now,
                updated_at=now,
                last_used_at=None,
                source=request.source,
                metadata=dict(request.metadata),
            )
        return MemoryRecord(
            id=matched.id,
            text=request.text,
            type=request.type,
            scope=request.scope,
            salience=matched.salience if request.salience is None else request.salience,
            created_at=matched.created_at,
            updated_at=now,
            last_used_at=matched.last_used_at,
            source=request.source,
            embedding=matched.embedding,
            metadata={**dict(matched.metadata), **dict(request.metadata)},
        )


@dataclass(slots=True)
class KnowledgeApplicationService:
    """Application service for knowledge records and explicit links."""

    unit_of_work: PersistenceUnitOfWork
    clock: Clock = _utc_now
    id_generator: IdGenerator = _new_id

    def capture(self, request: CaptureKnowledgeRequest) -> KnowledgeRecord:
        now = self.clock()
        record = KnowledgeRecord(
            id=self.id_generator(),
            title=request.title,
            text=request.text,
            kind=request.kind,
            created_at=now,
            updated_at=now,
            source=request.source,
            metadata=dict(request.metadata),
        )
        try:
            saved = self.unit_of_work.knowledge.save(record)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise
        return saved

    def search(self, request: SearchKnowledgeRequest) -> Sequence[KnowledgeRecord]:
        return self.unit_of_work.knowledge.search(
            KnowledgeSearchQuery(
                text=request.text,
                limit=request.limit,
                related_to=request.related_to,
            )
        )

    def link(self, request: LinkKnowledgeItemsRequest) -> KnowledgeLinkRecord:
        link = KnowledgeLinkRecord(
            id=self.id_generator(),
            left_id=request.left_id,
            right_id=request.right_id,
            relation=request.relation,
            created_at=self.clock(),
            metadata=dict(request.metadata),
        )
        try:
            saved = self.unit_of_work.knowledge.save_link(link)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise
        return saved


@dataclass(slots=True)
class ExecutionApplicationService:
    """Application service for workflow-neutral execution records."""

    unit_of_work: PersistenceUnitOfWork
    clock: Clock = _utc_now
    id_generator: IdGenerator = _new_id

    def save(self, request: SaveExecutionRequest) -> ExecutionRecord:
        now = self.clock()
        record = ExecutionRecord(
            id=self.id_generator(),
            title=request.title,
            kind=request.kind,
            state=request.state,
            created_at=now,
            updated_at=now,
            source=request.source,
            project_id=request.project_id,
            due_at=request.due_at,
            review_at=request.review_at,
            metadata=dict(request.metadata),
        )
        try:
            saved = self.unit_of_work.execution.save(record)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise
        return saved

    def search(self, request: SearchExecutionRequest) -> Sequence[ExecutionRecord]:
        return self.unit_of_work.execution.search(
            ExecutionQuery(
                limit=request.limit,
                states=request.states,
                project_id=request.project_id,
                due_before=request.due_before,
                review_before=request.review_before,
            )
        )

    def list_review_queue(
        self, request: ReviewQueueRequest
    ) -> Sequence[ExecutionRecord]:
        return self.unit_of_work.execution.list_due_for_review(
            reference_at=request.reference_at,
            limit=request.limit,
        )


@dataclass(slots=True)
class ContextBundleApplicationService:
    """Application service for bounded cross-domain agent context."""

    memory_service: MemoryApplicationService
    knowledge_service: KnowledgeApplicationService
    execution_service: ExecutionApplicationService
    memory_query_embedding_provider: QueryEmbeddingProvider | None = None

    def get_bundle(self, request: ContextBundleRequest) -> ContextBundle:
        query_embedding = resolve_query_embedding(
            request.query,
            self.memory_query_embedding_provider,
        )
        return ContextBundle(
            memories=self.memory_service.search(
                SearchMemoryRequest(
                    text=request.query,
                    limit=request.memory_limit,
                    query_embedding=query_embedding,
                )
            ),
            knowledge=self.knowledge_service.search(
                SearchKnowledgeRequest(
                    text=request.query,
                    limit=request.knowledge_limit,
                )
            ),
            execution=self.execution_service.search(
                SearchExecutionRequest(limit=request.execution_limit)
            ),
        )


@dataclass(slots=True)
class VeraBrainApplication:
    """Convenience facade over the first callable application services."""

    unit_of_work: PersistenceUnitOfWork
    clock: Clock = _utc_now
    id_generator: IdGenerator = _new_id
    memory_embedding_provider: MemoryEmbeddingProvider | None = None
    memory_query_embedding_provider: QueryEmbeddingProvider | None = None
    memory: MemoryApplicationService = field(init=False)
    knowledge: KnowledgeApplicationService = field(init=False)
    execution: ExecutionApplicationService = field(init=False)
    context: ContextBundleApplicationService = field(init=False)

    def __post_init__(self) -> None:
        self.memory = MemoryApplicationService(
            unit_of_work=self.unit_of_work,
            clock=self.clock,
            id_generator=self.id_generator,
            memory_embedding_provider=self.memory_embedding_provider,
        )
        self.knowledge = KnowledgeApplicationService(
            unit_of_work=self.unit_of_work,
            clock=self.clock,
            id_generator=self.id_generator,
        )
        self.execution = ExecutionApplicationService(
            unit_of_work=self.unit_of_work,
            clock=self.clock,
            id_generator=self.id_generator,
        )
        self.context = ContextBundleApplicationService(
            memory_service=self.memory,
            knowledge_service=self.knowledge,
            execution_service=self.execution,
            memory_query_embedding_provider=self.memory_query_embedding_provider,
        )
