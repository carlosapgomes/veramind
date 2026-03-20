from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

from verabrain.adapters.mcp import MCPApplicationAdapter
from verabrain.application import (
    EMBEDDING_ERROR_METADATA_KEY,
    EMBEDDING_STATUS_METADATA_KEY,
    MemoryEmbeddingProvider,
    VeraBrainApplication,
)
from verabrain.application.ports import MemoryRecord
from verabrain.infrastructure import InMemoryMemoryRepository, InMemoryUnitOfWork


def _now() -> datetime:
    return datetime(2026, 3, 20, 12, 0, tzinfo=UTC)


def _id_sequence() -> Iterator[str]:
    for value in ("mem-1", "mem-2", "mem-3"):
        yield value


class StubMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return (0.1, 0.2, 0.3)


class FailingMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        raise RuntimeError("embedding backend unavailable")


class FailingInMemoryMemoryRepository(InMemoryMemoryRepository):
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        raise RuntimeError("storage unavailable")


class FailingInMemoryUnitOfWork(InMemoryUnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self._memories = FailingInMemoryMemoryRepository(self._current_workspace)


def _build_adapter(
    *,
    unit_of_work: InMemoryUnitOfWork | None = None,
    provider: MemoryEmbeddingProvider | None = None,
) -> MCPApplicationAdapter:
    ids = _id_sequence()
    application = VeraBrainApplication(
        unit_of_work=unit_of_work or InMemoryUnitOfWork(),
        clock=_now,
        id_generator=lambda: next(ids),
        memory_embedding_provider=provider or StubMemoryEmbeddingProvider(),
    )
    return MCPApplicationAdapter(application=application)


def test_memory_loop_mvp_captures_persists_and_retrieves_memory_through_mcp() -> None:
    adapter = _build_adapter()

    save_response = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
        },
    )

    assert save_response["ok"] is True
    saved = save_response["result"]
    assert isinstance(saved, dict)
    assert saved["id"] == "mem-1"
    assert saved["embedding"] == [0.1, 0.2, 0.3]

    search_response = adapter.dispatch(
        "search_memory",
        {"text": "concise", "limit": 1},
    )

    assert search_response["ok"] is True
    search_result = search_response["result"]
    assert isinstance(search_result, dict)
    items = search_result["items"]
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["id"] == "mem-1"

    bundle_response = adapter.dispatch(
        "get_context_bundle",
        {"query": "concise", "memory_limit": 1},
    )

    assert bundle_response["ok"] is True
    bundle_result = bundle_response["result"]
    assert isinstance(bundle_result, dict)
    memories = bundle_result["memories"]
    assert isinstance(memories, list)
    assert len(memories) == 1
    assert memories[0]["id"] == "mem-1"


def test_memory_loop_mvp_keeps_retrieval_bounded_through_mcp() -> None:
    adapter = _build_adapter()

    first_save = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
        },
    )
    second_save = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise project updates.",
            "type": "project",
            "scope": "medium",
            "source": "manual",
        },
    )

    assert first_save["ok"] is True
    assert second_save["ok"] is True

    search_response = adapter.dispatch(
        "search_memory",
        {"text": "user", "limit": 1},
    )

    assert search_response["ok"] is True
    search_result = search_response["result"]
    assert isinstance(search_result, dict)
    items = search_result["items"]
    assert isinstance(items, list)
    assert len(items) == 1

    bundle_response = adapter.dispatch(
        "get_context_bundle",
        {"query": "user", "memory_limit": 1},
    )

    assert bundle_response["ok"] is True
    bundle_result = bundle_response["result"]
    assert isinstance(bundle_result, dict)
    memories = bundle_result["memories"]
    assert isinstance(memories, list)
    assert len(memories) == 1


def test_memory_loop_mvp_reports_saved_without_embedding_through_mcp() -> None:
    adapter = _build_adapter(provider=FailingMemoryEmbeddingProvider())

    save_response = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
        },
    )

    assert save_response["ok"] is True
    saved = save_response["result"]
    assert isinstance(saved, dict)
    assert saved["embedding"] is None
    metadata = saved["metadata"]
    assert isinstance(metadata, dict)
    assert metadata == {
        EMBEDDING_STATUS_METADATA_KEY: "failed",
        EMBEDDING_ERROR_METADATA_KEY: "RuntimeError",
    }

    search_response = adapter.dispatch(
        "search_memory",
        {"text": "concise", "limit": 1},
    )

    assert search_response["ok"] is True
    search_result = search_response["result"]
    assert isinstance(search_result, dict)
    items = search_result["items"]
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["metadata"] == {
        EMBEDDING_STATUS_METADATA_KEY: "failed",
        EMBEDDING_ERROR_METADATA_KEY: "RuntimeError",
    }


def test_memory_loop_mvp_reports_save_failed_when_persistence_degrades() -> None:
    adapter = _build_adapter(unit_of_work=FailingInMemoryUnitOfWork())

    save_response = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
        },
    )

    assert save_response == {
        "ok": False,
        "tool": "save_memory",
        "error": {
            "code": "application_error",
            "message": "storage unavailable",
        },
    }

    search_response = adapter.dispatch(
        "search_memory",
        {"text": "concise", "limit": 1},
    )

    assert search_response["ok"] is True
    search_result = search_response["result"]
    assert isinstance(search_result, dict)
    items = search_result["items"]
    assert isinstance(items, list)
    assert items == []
