from __future__ import annotations

from dataclasses import dataclass

import pytest

from typing import cast

from verabrain.infrastructure import (
    OpenAIEmbeddingProvider,
    OpenAIEmbeddingProviderUnavailableError,
    OpenAIEmbeddingRuntimeConfigurationError,
    OpenAIEmbeddingRuntimeSettings,
    load_default_openai_client_factory,
)
import verabrain.infrastructure.openai_embeddings as openai_embeddings
from verabrain.infrastructure.openai_embeddings import OpenAIClientFactory


class RecordingEmbeddingsEndpoint:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, *, model: str, input: str) -> object:
        self.calls.append({"model": model, "input": input})
        return {"data": [{"embedding": [0.1, 0.2, 0.3]}]}


@dataclass
class RecordingClient:
    embeddings: RecordingEmbeddingsEndpoint


class RecordingClientFactory:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.endpoint = RecordingEmbeddingsEndpoint()

    def __call__(self, **kwargs: object) -> RecordingClient:
        self.calls.append(dict(kwargs))
        return RecordingClient(embeddings=self.endpoint)


def test_openai_embedding_settings_allow_disabled_runtime() -> None:
    settings = OpenAIEmbeddingRuntimeSettings()

    assert settings.enabled is False
    assert settings.client_kwargs() == {}


def test_openai_embedding_settings_require_api_key_and_model_together() -> None:
    with pytest.raises(
        OpenAIEmbeddingRuntimeConfigurationError,
        match="require both api_key and model",
    ):
        OpenAIEmbeddingRuntimeSettings(api_key="test-key")

    with pytest.raises(
        OpenAIEmbeddingRuntimeConfigurationError,
        match="require both api_key and model",
    ):
        OpenAIEmbeddingRuntimeSettings(model="text-embedding-3-small")


def test_openai_embedding_settings_normalize_and_build_client_kwargs() -> None:
    settings = OpenAIEmbeddingRuntimeSettings(
        api_key=" test-key ",
        model=" text-embedding-3-small ",
        base_url=" https://example.test/v1 ",
    )

    assert settings.enabled is True
    assert settings.api_key == "test-key"
    assert settings.model == "text-embedding-3-small"
    assert settings.base_url == "https://example.test/v1"
    assert settings.client_kwargs() == {
        "api_key": "test-key",
        "base_url": "https://example.test/v1",
    }


def test_openai_embedding_provider_returns_none_when_disabled() -> None:
    provider = OpenAIEmbeddingProvider(OpenAIEmbeddingRuntimeSettings())

    assert provider.embed_memory_text("Remember this") is None
    assert provider.embed_query_text("Remember this") is None


def test_openai_embedding_provider_uses_client_factory_for_write_and_query_embeddings() -> None:
    factory = RecordingClientFactory()
    provider = OpenAIEmbeddingProvider(
        OpenAIEmbeddingRuntimeSettings(
            api_key="test-key",
            model="text-embedding-3-small",
            base_url="https://example.test/v1",
        ),
        client_factory=cast(OpenAIClientFactory, factory),
    )

    write_embedding = provider.embed_memory_text("Remember this")
    query_embedding = provider.embed_query_text("Find this")

    assert write_embedding == (0.1, 0.2, 0.3)
    assert query_embedding == (0.1, 0.2, 0.3)
    assert factory.calls == [{"api_key": "test-key", "base_url": "https://example.test/v1"}]
    assert factory.endpoint.calls == [
        {"model": "text-embedding-3-small", "input": "Remember this"},
        {"model": "text-embedding-3-small", "input": "Find this"},
    ]


def test_load_default_openai_client_factory_raises_when_sdk_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_module(_name: str) -> object:
        raise ModuleNotFoundError("openai")

    monkeypatch.setattr(openai_embeddings, "import_module", missing_module)

    with pytest.raises(
        OpenAIEmbeddingProviderUnavailableError,
        match="openai is required",
    ):
        load_default_openai_client_factory()
