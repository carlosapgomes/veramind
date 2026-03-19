"""Adapter-neutral embedding boundaries for VeraBrain application services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

EMBEDDING_STATUS_METADATA_KEY = "verabrain_embedding_status"
EMBEDDING_ERROR_METADATA_KEY = "verabrain_embedding_error"
MemoryEmbeddingStatus = Literal["generated", "unavailable", "failed"]


class MemoryEmbeddingProvider(Protocol):
    """Generates embeddings for memory capture without backend coupling."""

    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        """Return an embedding for memory capture or ``None`` when unavailable."""


@dataclass(frozen=True, slots=True)
class MemoryEmbeddingCaptureResult:
    """Outcome of embedding capture for a memory write attempt."""

    status: MemoryEmbeddingStatus
    embedding: tuple[float, ...] | None = None
    error_type: str | None = None

    def metadata(self) -> dict[str, object]:
        """Return namespaced metadata that makes capture fallback observable."""

        result: dict[str, object] = {EMBEDDING_STATUS_METADATA_KEY: self.status}
        if self.error_type is not None:
            result[EMBEDDING_ERROR_METADATA_KEY] = self.error_type
        return result


def resolve_memory_embedding(
    text: str,
    provider: MemoryEmbeddingProvider | None,
) -> MemoryEmbeddingCaptureResult:
    """Resolve a memory embedding without leaking provider failures downstream."""

    if provider is None:
        return MemoryEmbeddingCaptureResult(status="unavailable")
    try:
        embedding = provider.embed_memory_text(text)
    except Exception as exc:
        return MemoryEmbeddingCaptureResult(
            status="failed",
            error_type=type(exc).__name__,
        )
    if embedding is None:
        return MemoryEmbeddingCaptureResult(status="unavailable")
    return MemoryEmbeddingCaptureResult(status="generated", embedding=embedding)
