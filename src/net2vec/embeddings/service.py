"""Embedding orchestration."""

from __future__ import annotations

from net2vec.embeddings.client import EmbeddingClient


class EmbeddingService:
    def __init__(self, client: EmbeddingClient, model: str, dimensions: int) -> None:
        self.client = client
        self.model = model
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[tuple[float, ...]]:
        vectors = self.client.embed(texts, self.model)
        return [_validate_vector(vector, self.dimensions) for vector in vectors]


def _validate_vector(vector: list[float], dimensions: int) -> tuple[float, ...]:
    if len(vector) != dimensions:
        raise ValueError(f"expected embedding dimension {dimensions}, got {len(vector)}")
    return tuple(float(value) for value in vector)
