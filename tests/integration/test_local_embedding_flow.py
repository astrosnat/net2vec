from net2vec.config.settings import Settings
from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.factory import create_embedding_service
from net2vec.ingestion.fetcher import FetchResult
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.repositories import InMemoryDocumentRepository
from net2vec.search.service import SearchService


class FakeLocalClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [_vector_for(text) for text in texts]


class FakeFetcher:
    def fetch(self, url: str) -> FetchResult:
        html = "<h1>Names</h1><p>MixedCaps are preferred in Go names.</p>"
        return FetchResult(url=url, html=html, status_code=200)


def test_local_provider_ingests_and_searches_without_openai_key() -> None:
    settings = _settings(provider="local", api_key=None)
    repo = InMemoryDocumentRepository()
    embeddings = create_embedding_service(settings, local_factory=FakeLocalClient)
    pipeline = IngestionPipeline(FakeFetcher(), embeddings, repo)

    result = pipeline.ingest("https://go.dev/doc/effective_go")
    response = SearchService(embeddings, repo).search("mixed caps", limit=1)

    assert result.sections[0].embedding_model == "fake-model"
    assert result.sections[0].embedding_dimensions == 3
    assert response.results[0].source_url == "https://go.dev/doc/effective_go"
    assert response.results[0].score == 1.0


def _vector_for(text: str) -> list[float]:
    if "mixed" in text.lower():
        return [1.0, 0.0, 0.0]
    return [0.0, 1.0, 0.0]


def _settings(provider: str, api_key: str | None = None) -> Settings:
    return Settings(
        database_url="postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec",
        openai_api_key=api_key,
        embedding_provider=provider,
        embedding_model="fake-model",
        embedding_dimensions=3,
        api_host="127.0.0.1",
        api_port=8000,
        mcp_url="http://127.0.0.1:8001/mcp",
    )
