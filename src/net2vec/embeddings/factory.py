"""Embedding provider selection."""

from __future__ import annotations

from collections.abc import Callable

from net2vec.config.settings import LOCAL_EMBEDDING_PROVIDER, OPENAI_EMBEDDING_PROVIDER, Settings
from net2vec.embeddings.client import EmbeddingClient, LocalEmbeddingClient, OpenAIEmbeddingClient
from net2vec.embeddings.service import EmbeddingService

ClientFactory = Callable[[], EmbeddingClient]
OpenAIClientFactory = Callable[[str | None], EmbeddingClient]


def create_embedding_service(
    settings: Settings,
    local_factory: ClientFactory = LocalEmbeddingClient,
    openai_factory: OpenAIClientFactory = OpenAIEmbeddingClient,
) -> EmbeddingService:
    return EmbeddingService(
        create_embedding_client(settings, local_factory, openai_factory),
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )


def create_embedding_client(
    settings: Settings,
    local_factory: ClientFactory = LocalEmbeddingClient,
    openai_factory: OpenAIClientFactory = OpenAIEmbeddingClient,
) -> EmbeddingClient:
    if settings.embedding_provider == LOCAL_EMBEDDING_PROVIDER:
        return local_factory()
    if settings.embedding_provider == OPENAI_EMBEDDING_PROVIDER:
        return openai_factory(settings.openai_api_key)
    raise ValueError(f"unsupported embedding provider {settings.embedding_provider!r}")
