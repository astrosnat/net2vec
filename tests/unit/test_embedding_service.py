import pytest

from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.service import EmbeddingService


class FakeClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_embeds_texts_with_dimension_validation() -> None:
    service = EmbeddingService(FakeClient(), model="fake", dimensions=3)

    assert service.embed_texts(["one", "two"]) == [(1.0, 0.0, 0.0), (1.0, 0.0, 0.0)]


def test_rejects_unexpected_dimensions() -> None:
    service = EmbeddingService(FakeClient(), model="fake", dimensions=2)

    with pytest.raises(ValueError):
        service.embed_texts(["one"])
