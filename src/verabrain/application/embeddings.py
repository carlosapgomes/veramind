"""Adapter-neutral embedding boundaries for VeraBrain application services."""

from __future__ import annotations

from typing import Protocol


class MemoryEmbeddingProvider(Protocol):
    """Generates embeddings for memory capture without backend coupling."""

    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        """Return an embedding for memory capture or ``None`` when unavailable."""
