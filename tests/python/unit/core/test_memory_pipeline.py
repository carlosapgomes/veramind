from verabrain.core import classify_memory_write


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
