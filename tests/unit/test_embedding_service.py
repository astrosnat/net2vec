import pytest

from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.service import EmbeddingService


class FakeClient(EmbeddingClient):
    def __init__(self) -> None:
        self.requests: list[list[str]] = []

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        self.requests.append(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_embeds_texts_with_dimension_validation() -> None:
    service = EmbeddingService(FakeClient(), model="fake", dimensions=3)

    assert service.embed_texts(["one", "two"]) == [(1.0, 0.0, 0.0), (1.0, 0.0, 0.0)]


def test_rejects_unexpected_dimensions() -> None:
    service = EmbeddingService(FakeClient(), model="fake", dimensions=2)

    with pytest.raises(ValueError):
        service.embed_texts(["one"])


def test_embed_query_reuses_text_embedding_path() -> None:
    client = FakeClient()
    service = EmbeddingService(client, model="fake", dimensions=3)

    assert service.embed_query("question") == (1.0, 0.0, 0.0)
    assert client.requests == [["question"]]
