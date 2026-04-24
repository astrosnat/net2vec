from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.fetcher import FetchResult
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.repositories import InMemoryDocumentRepository


class FakeClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [[float(index), 0.0, 1.0] for index, _ in enumerate(texts)]


class FakeFetcher:
    def __init__(self) -> None:
        self.html = "<h1>Names</h1><p>MixedCaps are preferred.</p>"

    def fetch(self, url: str) -> FetchResult:
        return FetchResult(url=url, html=self.html, status_code=200)


def test_ingest_then_refresh_replaces_active_content() -> None:
    fetcher = FakeFetcher()
    repo = InMemoryDocumentRepository()
    pipeline = IngestionPipeline(
        fetcher=fetcher,
        embedding_service=EmbeddingService(FakeClient(), model="fake", dimensions=3),
        repository=repo,
    )

    first = pipeline.ingest("https://go.dev/doc/effective_go")
    fetcher.html = "<h1>Names</h1><p>Initialisms stay consistent.</p>"
    second = pipeline.ingest("https://go.dev/doc/effective_go")

    sections = repo.active_sections(second.document.id)
    assert first.document.id != second.document.id
    assert repo.active_sections(first.document.id) == []
    assert sections[0].heading_path == ("Names",)
    assert sections[0].full_chunk_text == "Initialisms stay consistent."
