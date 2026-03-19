from datetime import UTC, datetime

from verabrain.application import MemoryRecord
from verabrain.core import (
    assess_memory_duplicate,
    classify_memory_write,
    memory_duplicate_score,
)


def test_memory_write_classification_ignores_empty_input() -> None:
    result = classify_memory_write("   ")

    assert result.disposition == "ignore"
    assert result.reason == "empty_text"
    assert result.normalized_text == ""


def test_memory_write_classification_ignores_transient_messages() -> None:
    result = classify_memory_write("thanks")

    assert result.disposition == "ignore"
    assert result.reason == "transient_message"


def test_memory_write_classification_ignores_non_durable_questions() -> None:
    result = classify_memory_write("Can you summarize this?")

    assert result.disposition == "ignore"
    assert result.reason == "non_durable_question"


def test_memory_write_classification_marks_durable_preferences_as_candidates() -> None:
    result = classify_memory_write("User prefers concise answers during project updates.")

    assert result.disposition == "memory_candidate"
    assert result.reason == "durable_signal"


def test_memory_write_classification_marks_first_person_context_as_candidates() -> None:
    result = classify_memory_write("I work better in the morning when planning my week.")

    assert result.disposition == "memory_candidate"
    assert result.reason == "first_person_context"


def test_memory_duplicate_score_detects_materially_identical_text() -> None:
    score = memory_duplicate_score(
        "User prefers concise answers!",
        "user prefers concise answers.",
    )

    assert score == 1.0


def test_memory_duplicate_assessment_returns_matching_existing_memory() -> None:
    candidate = MemoryRecord(
        id="mem-1",
        text="User prefers concise answers.",
        type="preference",
        scope="long",
        salience=0.9,
        created_at=datetime(2026, 3, 19, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 3, 19, 12, 0, tzinfo=UTC),
        last_used_at=None,
        source="manual",
    )

    result = assess_memory_duplicate(
        "User prefers concise answers!",
        (candidate,),
    )

    assert result.matched_record == candidate
    assert result.score == 1.0


def test_memory_duplicate_assessment_rejects_weak_matches() -> None:
    candidate = MemoryRecord(
        id="mem-2",
        text="User likes detailed weekend plans.",
        type="habit",
        scope="medium",
        salience=0.4,
        created_at=datetime(2026, 3, 19, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 3, 19, 12, 0, tzinfo=UTC),
        last_used_at=None,
        source="manual",
    )

    result = assess_memory_duplicate(
        "Project timeline depends on Hermes MCP delivery.",
        (candidate,),
    )

    assert result.matched_record is None
    assert result.score == 0.0
