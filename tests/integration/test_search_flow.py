from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.fetcher import FetchResult
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.repositories import InMemoryDocumentRepository
from net2vec.search.service import SearchService


class FakeClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [_vector_for(text) for text in texts]


class FakeFetcher:
    def fetch(self, url: str) -> FetchResult:
        html = "<h1>Names</h1><p>MixedCaps are preferred in Go names.</p>"
        return FetchResult(url=url, html=html, status_code=200)


def test_ingest_then_semantic_search_returns_source_grounded_result() -> None:
    repo = InMemoryDocumentRepository()
    embeddings = EmbeddingService(FakeClient(), model="fake", dimensions=3)
    pipeline = IngestionPipeline(FakeFetcher(), embeddings, repo)
    pipeline.ingest("https://go.dev/doc/effective_go")

    response = SearchService(embeddings, repo).search(
        "When should Go code use mixed caps?",
        limit=3,
    )

    assert response.no_match_reason is None
    assert response.results[0].source_url == "https://go.dev/doc/effective_go"
    assert response.results[0].heading_path == ("Names",)
    assert response.results[0].excerpt == "MixedCaps are preferred in Go names."
    assert response.results[0].full_chunk_text == "MixedCaps are preferred in Go names."
    assert response.results[0].rank == 1
    assert response.results[0].score == 1.0


def _vector_for(text: str) -> list[float]:
    if "mixed" in text.lower():
        return [1.0, 0.0, 0.0]
    return [0.0, 1.0, 0.0]
