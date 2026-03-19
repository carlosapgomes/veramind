"""Core memory-write pipeline rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

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


def _contains_durable_signal(text: str) -> bool:
    return any(signal in text for signal in _DURABLE_SIGNALS)


def _contains_first_person_context(text: str) -> bool:
    padded = f" {text} "
    return len(text.split()) >= 4 and any(marker in padded for marker in _FIRST_PERSON_MARKERS)
