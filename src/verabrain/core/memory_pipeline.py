"""Core memory-write pipeline rules."""

from __future__ import annotations

from dataclasses import dataclass
from string import punctuation
from typing import TYPE_CHECKING, Literal, Sequence

if TYPE_CHECKING:
    from verabrain.application.ports import MemoryRecord

MemoryWriteDisposition = Literal["memory_candidate", "ignore"]

_TRANSIENT_MESSAGES = frozenset(
    {
        "hi",
        "hello",
        "hey",
        "ok",
        "okay",
        "thanks",
        "thank you",
        "cool",
        "got it",
    }
)
_DURABLE_SIGNALS = (
    "prefer",
    "like ",
    "likes ",
    "dislike",
    "decision",
    "decided",
    "project",
    "habit",
    "follow up",
    "follow-up",
    "profile",
    "remember",
    "always",
    "usually",
    "never",
    "my name",
    "i am",
    "i'm",
)
_FIRST_PERSON_MARKERS = (" i ", " my ", " me ", " we ", " our ")


@dataclass(frozen=True, slots=True)
class MemoryWriteClassification:
    """Classification result for the initial memory write boundary."""

    disposition: MemoryWriteDisposition
    reason: str
    normalized_text: str


@dataclass(frozen=True, slots=True)
class MemoryDuplicateAssessment:
    """Duplicate-assessment result for a memory write candidate."""

    matched_record: MemoryRecord | None
    score: float


def classify_memory_write(text: str) -> MemoryWriteClassification:
    """Classify whether input belongs in the durable memory write path."""

    normalized = " ".join(text.split())
    if not normalized:
        return MemoryWriteClassification(
            disposition="ignore",
            reason="empty_text",
            normalized_text="",
        )

    lowered = normalized.lower()
    stripped = lowered.rstrip(".!?")
    if stripped in _TRANSIENT_MESSAGES:
        return MemoryWriteClassification(
            disposition="ignore",
            reason="transient_message",
            normalized_text=normalized,
        )

    if lowered.endswith("?") and not _contains_durable_signal(lowered):
        return MemoryWriteClassification(
            disposition="ignore",
            reason="non_durable_question",
            normalized_text=normalized,
        )

    if _contains_durable_signal(lowered):
        return MemoryWriteClassification(
            disposition="memory_candidate",
            reason="durable_signal",
            normalized_text=normalized,
        )

    if _contains_first_person_context(lowered):
        return MemoryWriteClassification(
            disposition="memory_candidate",
            reason="first_person_context",
            normalized_text=normalized,
        )

    return MemoryWriteClassification(
        disposition="ignore",
        reason="no_durable_signal",
        normalized_text=normalized,
    )


def assess_memory_duplicate(
    text: str,
    candidates: Sequence[MemoryRecord],
    *,
    threshold: float = 0.85,
) -> MemoryDuplicateAssessment:
    """Return the strongest duplicate match for a memory candidate."""

    best_record: MemoryRecord | None = None
    best_score = 0.0
    for candidate in candidates:
        score = memory_duplicate_score(text, candidate.text)
        if score > best_score:
            best_score = score
            best_record = candidate
    if best_record is None or best_score < threshold:
        return MemoryDuplicateAssessment(matched_record=None, score=best_score)
    return MemoryDuplicateAssessment(matched_record=best_record, score=best_score)


def memory_duplicate_score(candidate_text: str, existing_text: str) -> float:
    """Return a deterministic duplicate score for memory write deduplication."""

    normalized_candidate = _normalize_memory_text(candidate_text)
    normalized_existing = _normalize_memory_text(existing_text)
    if not normalized_candidate or not normalized_existing:
        return 0.0
    if normalized_candidate == normalized_existing:
        return 1.0

    candidate_tokens = set(normalized_candidate.split())
    existing_tokens = set(normalized_existing.split())
    overlap = candidate_tokens & existing_tokens
    return len(overlap) / max(len(candidate_tokens), len(existing_tokens))


def _contains_durable_signal(text: str) -> bool:
    return any(signal in text for signal in _DURABLE_SIGNALS)


def _contains_first_person_context(text: str) -> bool:
    padded = f" {text} "
    return len(text.split()) >= 4 and any(marker in padded for marker in _FIRST_PERSON_MARKERS)


def _normalize_memory_text(text: str) -> str:
    translation = str.maketrans("", "", punctuation)
    return " ".join(text.casefold().translate(translation).split())
