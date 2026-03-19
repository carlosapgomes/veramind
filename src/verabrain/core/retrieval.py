"""Core-owned retrieval scoring helpers for VeraBrain."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from verabrain.application.ports import MemoryRecord

_MEMORY_TYPE_WEIGHTS = {
    "decision": 1.15,
    "project": 1.05,
    "preference": 1.0,
    "followup": 0.95,
    "profile": 0.9,
    "habit": 0.85,
}


@dataclass(frozen=True, slots=True)
class MemoryRetrievalCandidate:
    """Candidate memory with adapter-provided retrieval signals."""

    record: MemoryRecord
    lexical_score: float | None = None
    semantic_score: float | None = None


def memory_candidate_limit(limit: int) -> int:
    """Expand a requested result limit into a bounded candidate pool size."""

    return min(max(limit * 4, 10), 50)


def resolve_query_embedding(
    query_text: str,
    provider: Callable[[str], tuple[float, ...] | None] | None,
) -> tuple[float, ...] | None:
    """Resolve semantic input safely, falling back to lexical-only retrieval."""

    if provider is None:
        return None
    try:
        return provider(query_text)
    except Exception:
        return None


def rerank_memory_candidates(
    candidates: tuple[MemoryRetrievalCandidate, ...],
    *,
    query_text: str,
    limit: int,
) -> tuple[MemoryRecord, ...]:
    """Rerank candidate memories using the current hybrid retrieval policy."""

    scored: list[tuple[tuple[float, float, float, float, str], MemoryRecord]] = []
    for candidate in candidates:
        scored.append(
            (
                memory_rank_key(candidate, query_text=query_text),
                candidate.record,
            )
        )
    scored.sort(key=lambda item: item[0], reverse=True)
    return tuple(record for _, record in scored[:limit])


def memory_rank_key(
    candidate: MemoryRetrievalCandidate,
    *,
    query_text: str,
) -> tuple[float, float, float, float, str]:
    """Return a deterministic ranking key for a memory candidate."""

    lexical_score = _coerce_score(
        candidate.lexical_score,
        fallback=text_overlap_score(query_text, candidate.record.text),
    )
    semantic_score = _coerce_score(candidate.semantic_score, fallback=0.0)
    type_weight = _MEMORY_TYPE_WEIGHTS.get(candidate.record.type, 0.8)
    recency_reference = candidate.record.last_used_at or candidate.record.updated_at
    return (
        semantic_score,
        lexical_score + candidate.record.salience + type_weight,
        recency_reference.timestamp(),
        candidate.record.updated_at.timestamp(),
        candidate.record.id,
    )


def text_overlap_score(query_text: str, candidate_text: str) -> float:
    """Return a simple lexical overlap score for fallback retrieval."""

    normalized_query = set(" ".join(query_text.casefold().split()).split())
    normalized_candidate = set(" ".join(candidate_text.casefold().split()).split())
    if not normalized_query or not normalized_candidate:
        return 0.0
    return sum(1.0 for token in normalized_query if token in normalized_candidate)


def _coerce_score(value: float | None, *, fallback: float) -> float:
    if value is None:
        return fallback
    return float(value)
