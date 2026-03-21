"""OpenAI-backed embedding runtime boundary for the local MVP path."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Callable, Mapping, Protocol, Sequence, cast


class OpenAIEmbeddingRuntimeConfigurationError(ValueError):
    """Raised when OpenAI embedding settings are incomplete or invalid."""


class OpenAIEmbeddingProviderUnavailableError(RuntimeError):
    """Raised when the OpenAI embedding provider cannot be constructed."""


@dataclass(frozen=True, slots=True)
class OpenAIEmbeddingRuntimeSettings:
    """Explicit settings for the OpenAI-backed embedding runtime path."""

    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None

    def __post_init__(self) -> None:
        normalized_api_key = _clean(self.api_key)
        normalized_model = _clean(self.model)
        normalized_base_url = _clean(self.base_url)
        if (normalized_api_key is None) != (normalized_model is None):
            raise OpenAIEmbeddingRuntimeConfigurationError(
                "OpenAI embedding settings require both api_key and model when enabled."
            )
        object.__setattr__(self, "api_key", normalized_api_key)
        object.__setattr__(self, "model", normalized_model)
        object.__setattr__(self, "base_url", normalized_base_url)

    @property
    def enabled(self) -> bool:
        """Return whether the runtime should attempt provider-backed embeddings."""

        return self.api_key is not None and self.model is not None

    def client_kwargs(self) -> dict[str, object]:
        """Build the OpenAI client keyword arguments for this settings object."""

        if not self.enabled:
            return {}
        kwargs: dict[str, object] = {"api_key": self.api_key}
        if self.base_url is not None:
            kwargs["base_url"] = self.base_url
        return kwargs

    def require_model(self) -> str:
        """Return the configured model or raise when embeddings are disabled."""

        if self.model is None:
            raise OpenAIEmbeddingRuntimeConfigurationError(
                "OpenAI embedding settings are disabled and do not define a model."
            )
        return self.model


class OpenAIEmbeddingsEndpointProtocol(Protocol):
    """Minimal embeddings endpoint shape required by the provider."""

    def create(self, *, model: str, input: str) -> object:
        """Request one embedding for the given input text."""


class OpenAIClientProtocol(Protocol):
    """Minimal OpenAI client shape required by the provider."""

    embeddings: OpenAIEmbeddingsEndpointProtocol


OpenAIClientFactory = Callable[..., OpenAIClientProtocol]


def load_default_openai_client_factory() -> OpenAIClientFactory:
    """Load the default OpenAI client constructor lazily."""

    try:
        openai = import_module("openai")
    except ModuleNotFoundError as exc:
        raise OpenAIEmbeddingProviderUnavailableError(
            "openai is required for the OpenAI embedding runtime path."
        ) from exc
    client = getattr(openai, "OpenAI", None)
    if not callable(client):
        raise OpenAIEmbeddingProviderUnavailableError(
            "openai.OpenAI is not available for the embedding runtime path."
        )
    return cast(OpenAIClientFactory, client)


class OpenAIEmbeddingProvider:
    """Infrastructure-edge provider for OpenAI-backed memory embeddings."""

    def __init__(
        self,
        settings: OpenAIEmbeddingRuntimeSettings,
        *,
        client_factory: OpenAIClientFactory | None = None,
    ) -> None:
        self._settings = settings
        self._client_factory = client_factory
        self._client: OpenAIClientProtocol | None = None

    @property
    def settings(self) -> OpenAIEmbeddingRuntimeSettings:
        """Expose the settings behind this provider."""

        return self._settings

    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        """Generate a write-path embedding or return ``None`` when disabled."""

        return self._embed_text(text)

    def embed_query_text(self, text: str) -> tuple[float, ...] | None:
        """Generate a retrieval query embedding or return ``None`` when disabled."""

        return self._embed_text(text)

    def _embed_text(self, text: str) -> tuple[float, ...] | None:
        if not self._settings.enabled:
            return None
        response = self._client_or_create().embeddings.create(
            model=self._settings.require_model(),
            input=text,
        )
        return _extract_embedding(response)

    def _client_or_create(self) -> OpenAIClientProtocol:
        if self._client is None:
            factory = self._client_factory or load_default_openai_client_factory()
            try:
                self._client = factory(**self._settings.client_kwargs())
            except OpenAIEmbeddingProviderUnavailableError:
                raise
            except Exception as exc:
                raise OpenAIEmbeddingProviderUnavailableError(
                    "Unable to construct the OpenAI embedding client for the runtime path."
                ) from exc
        return self._client


def _extract_embedding(response: object) -> tuple[float, ...] | None:
    data = _field(response, "data")
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes, bytearray)):
        return None
    if not data:
        return None
    embedding = _field(data[0], "embedding")
    if not isinstance(embedding, Sequence) or isinstance(
        embedding, (str, bytes, bytearray)
    ):
        return None
    return tuple(float(value) for value in embedding)


def _field(value: object, name: str) -> object:
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
