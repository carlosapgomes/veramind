from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

from verabrain.adapters.mcp import MCPApplicationAdapter
from verabrain.application import MemoryEmbeddingProvider, VeraBrainApplication
from verabrain.application.ports import MemoryRecord
from verabrain.infrastructure import (
    InMemoryMemoryRepository,
    InMemoryPersistenceStore,
    InMemoryUnitOfWork,
)


def _now() -> datetime:
    return datetime(2026, 3, 20, 12, 0, tzinfo=UTC)


def _id_sequence() -> Iterator[str]:
    for value in ("mem-1", "mem-2", "mem-3"):
        yield value


class StubMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return (0.1, 0.2, 0.3)


class FailingInMemoryMemoryRepository(InMemoryMemoryRepository):
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        raise RuntimeError("storage unavailable")


class FailingInMemoryUnitOfWork(InMemoryUnitOfWork):
    def __init__(self, *, store: InMemoryPersistenceStore) -> None:
        super().__init__(store=store)
        self._memories = FailingInMemoryMemoryRepository(self._current_workspace)


def _build_adapter(
    *,
    store: InMemoryPersistenceStore,
    unit_of_work: InMemoryUnitOfWork | None = None,
) -> MCPApplicationAdapter:
    ids = _id_sequence()
    application = VeraBrainApplication(
        unit_of_work=unit_of_work or InMemoryUnitOfWork(store=store),
        clock=_now,
        id_generator=lambda: next(ids),
        memory_embedding_provider=StubMemoryEmbeddingProvider(),
    )
    return MCPApplicationAdapter(application=application)


def test_mcp_retrieval_surfaces_do_not_promote_memory_without_explicit_capture() -> None:
    store = InMemoryPersistenceStore()
    adapter = _build_adapter(store=store)

    search_response = adapter.dispatch("search_memory", {"text": "concise", "limit": 1})
    bundle_response = adapter.dispatch(
        "get_context_bundle",
        {"query": "concise", "memory_limit": 1},
    )

    assert search_response["ok"] is True
    assert bundle_response["ok"] is True
    assert store.memories == {}


def test_explicit_save_memory_transfers_durable_authority_into_verabrain_store() -> None:
    store = InMemoryPersistenceStore()
    adapter = _build_adapter(store=store)

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
    assert list(store.memories) == ["mem-1"]
    persisted = store.memories["mem-1"]
    assert persisted.text == "User prefers concise answers."
    assert persisted.embedding == (0.1, 0.2, 0.3)


def test_failed_explicit_capture_does_not_transfer_durable_authority() -> None:
    store = InMemoryPersistenceStore()
    adapter = _build_adapter(
        store=store,
        unit_of_work=FailingInMemoryUnitOfWork(store=store),
    )

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
    assert store.memories == {}
