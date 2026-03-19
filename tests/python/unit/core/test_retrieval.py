from __future__ import annotations

from datetime import UTC, datetime

from verabrain.application import MemoryRecord
from verabrain.core import (
    MemoryRetrievalCandidate,
    memory_candidate_limit,
    memory_rank_key,
    resolve_query_embedding,
    rerank_memory_candidates,
    text_overlap_score,
)


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


def _memory(
    *,
    record_id: str,
    text: str,
    memory_type: str,
    salience: float,
    updated_at: datetime | None = None,
    last_used_at: datetime | None = None,
) -> MemoryRecord:
    return MemoryRecord(
        id=record_id,
        text=text,
        type=memory_type,
        scope="long",
        salience=salience,
        created_at=_now(),
        updated_at=updated_at or _now(),
        last_used_at=last_used_at,
        source="manual",
    )


def test_memory_candidate_limit_expands_and_bounds_requested_results() -> None:
    assert memory_candidate_limit(1) == 10
    assert memory_candidate_limit(5) == 20
    assert memory_candidate_limit(20) == 50


def test_resolve_query_embedding_returns_none_without_provider_or_on_failure() -> None:
    assert resolve_query_embedding("Hermes", None) is None
    assert (
        resolve_query_embedding("Hermes", lambda query: (_ for _ in ()).throw(RuntimeError()))
        is None
    )


def test_text_overlap_score_uses_casefolded_token_overlap() -> None:
    assert text_overlap_score("Hermes runtime", "hermes runtime shell") == 2.0
    assert text_overlap_score("Hermes runtime", "other content") == 0.0


def test_rerank_memory_candidates_prefers_semantic_signal_before_lexical_ties() -> None:
    candidates = (
        MemoryRetrievalCandidate(
            record=_memory(
                record_id="mem-lexical",
                text="Hermes runtime notes",
                memory_type="preference",
                salience=0.9,
                updated_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
            ),
            lexical_score=2.0,
            semantic_score=0.2,
        ),
        MemoryRetrievalCandidate(
            record=_memory(
                record_id="mem-semantic",
                text="Long-term runtime shell context",
                memory_type="decision",
                salience=0.7,
                last_used_at=_now(),
            ),
            lexical_score=0.0,
            semantic_score=0.9,
        ),
    )

    results = rerank_memory_candidates(candidates, query_text="Hermes runtime", limit=1)

    assert [record.id for record in results] == ["mem-semantic"]


def test_rerank_memory_candidates_falls_back_to_lexical_salience_and_type_weight() -> None:
    candidates = (
        MemoryRetrievalCandidate(
            record=_memory(
                record_id="mem-project",
                text="Hermes project status context",
                memory_type="project",
                salience=0.7,
            )
        ),
        MemoryRetrievalCandidate(
            record=_memory(
                record_id="mem-habit",
                text="Hermes project status context",
                memory_type="habit",
                salience=0.7,
            )
        ),
    )

    results = rerank_memory_candidates(candidates, query_text="Hermes project", limit=2)

    assert [record.id for record in results] == ["mem-project", "mem-habit"]


def test_memory_rank_key_uses_last_used_at_as_the_primary_recency_signal() -> None:
    candidate = MemoryRetrievalCandidate(
        record=_memory(
            record_id="mem-1",
            text="Runtime shell context",
            memory_type="preference",
            salience=0.5,
            updated_at=datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
            last_used_at=datetime(2026, 3, 19, 10, 0, tzinfo=UTC),
        ),
        lexical_score=1.0,
    )

    rank_key = memory_rank_key(candidate, query_text="runtime shell")

    assert rank_key[2] == datetime(2026, 3, 19, 10, 0, tzinfo=UTC).timestamp()
