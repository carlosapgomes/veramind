"""Core domain layer for VeraBrain business concepts and rules."""

from .memory_pipeline import (
    ALLOWED_MEMORY_SCOPES,
    ALLOWED_MEMORY_TYPES,
    MemoryRecordValidationError,
    MemoryDuplicateAssessment,
    MemoryWriteClassification,
    assess_memory_duplicate,
    classify_memory_write,
    memory_duplicate_score,
    validate_memory_record_shape,
)
from .retrieval import (
    MemoryRetrievalCandidate,
    memory_candidate_limit,
    memory_rank_key,
    resolve_query_embedding,
    rerank_memory_candidates,
    text_overlap_score,
)

__all__ = [
    "MemoryRetrievalCandidate",
    "MemoryDuplicateAssessment",
    "MemoryRecordValidationError",
    "MemoryWriteClassification",
    "ALLOWED_MEMORY_SCOPES",
    "ALLOWED_MEMORY_TYPES",
    "assess_memory_duplicate",
    "classify_memory_write",
    "memory_candidate_limit",
    "memory_duplicate_score",
    "memory_rank_key",
    "resolve_query_embedding",
    "rerank_memory_candidates",
    "text_overlap_score",
    "validate_memory_record_shape",
]
