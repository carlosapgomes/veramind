from __future__ import annotations

from verabrain.application.embeddings import (
    EMBEDDING_DEDUPLICATION_ACTION_METADATA_KEY,
    EMBEDDING_ERROR_METADATA_KEY,
    EMBEDDING_STATUS_METADATA_KEY,
    MemoryEmbeddingCaptureResult,
    MemoryEmbeddingProvider,
    resolve_deduplicated_embedding,
    resolve_memory_embedding,
)


class StubMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return (0.1, 0.2, 0.3)


class NoneMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return None


class FailingMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        raise RuntimeError("embedding backend unavailable")


def test_capture_result_metadata_exposes_failed_status_and_error_type() -> None:
    result = MemoryEmbeddingCaptureResult(status="failed", error_type="RuntimeError")

    assert result.metadata() == {
        EMBEDDING_STATUS_METADATA_KEY: "failed",
        EMBEDDING_ERROR_METADATA_KEY: "RuntimeError",
    }


def test_resolve_memory_embedding_returns_generated_result() -> None:
    result = resolve_memory_embedding(
        "User prefers concise answers.",
        StubMemoryEmbeddingProvider(),
    )

    assert result.status == "generated"
    assert result.embedding == (0.1, 0.2, 0.3)
    assert result.metadata() == {EMBEDDING_STATUS_METADATA_KEY: "generated"}


def test_resolve_memory_embedding_returns_unavailable_result_when_provider_missing() -> None:
    result = resolve_memory_embedding("User prefers concise answers.", None)

    assert result.status == "unavailable"
    assert result.embedding is None
    assert result.metadata() == {EMBEDDING_STATUS_METADATA_KEY: "unavailable"}


def test_resolve_memory_embedding_returns_unavailable_result_when_provider_returns_none() -> None:
    result = resolve_memory_embedding(
        "User prefers concise answers.",
        NoneMemoryEmbeddingProvider(),
    )

    assert result.status == "unavailable"
    assert result.embedding is None
    assert result.metadata() == {EMBEDDING_STATUS_METADATA_KEY: "unavailable"}


def test_resolve_memory_embedding_returns_failed_result_when_provider_raises() -> None:
    result = resolve_memory_embedding(
        "User prefers concise answers.",
        FailingMemoryEmbeddingProvider(),
    )

    assert result.status == "failed"
    assert result.embedding is None
    assert result.error_type == "RuntimeError"
    assert result.metadata() == {
        EMBEDDING_STATUS_METADATA_KEY: "failed",
        EMBEDDING_ERROR_METADATA_KEY: "RuntimeError",
    }


def test_resolve_deduplicated_embedding_replaces_existing_embedding() -> None:
    result = resolve_deduplicated_embedding(
        (9.0, 9.0),
        MemoryEmbeddingCaptureResult(
            status="generated",
            embedding=(0.1, 0.2, 0.3),
        ),
    )

    assert result.embedding == (0.1, 0.2, 0.3)
    assert result.action == "replaced"
    assert result.metadata() == {
        EMBEDDING_DEDUPLICATION_ACTION_METADATA_KEY: "replaced"
    }


def test_resolve_deduplicated_embedding_preserves_existing_embedding() -> None:
    result = resolve_deduplicated_embedding(
        (9.0, 9.0),
        MemoryEmbeddingCaptureResult(status="unavailable"),
    )

    assert result.embedding == (9.0, 9.0)
    assert result.action == "preserved"
    assert result.metadata() == {
        EMBEDDING_DEDUPLICATION_ACTION_METADATA_KEY: "preserved"
    }
