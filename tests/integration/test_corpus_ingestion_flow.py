from net2vec.domain.corpus import (
    CorpusManifest,
    CorpusSource,
    CorpusSourceStatus,
    SourceClassification,
)
from net2vec.domain.documents import IngestionError
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.corpus import CorpusIngestionService
from net2vec.ingestion.fetcher import FetchResult
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.repositories import InMemoryDocumentRepository


class FakeClient:
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _text in texts]


class ManifestFetcher:
    def __init__(self) -> None:
        self.urls = []

    def fetch(self, url: str) -> FetchResult:
        self.urls.append(url)
        if url.endswith("unavailable"):
            raise IngestionError("URL fetch failed with status 503")
        html = '<main><h1>Rule</h1><p>Use this rule.</p><a href="https://unlisted.example">More</a></main>'
        return FetchResult(url=url, html=html, status_code=200)


def _source(identifier: str, enabled: bool = True) -> CorpusSource:
    return CorpusSource(
        identifier,
        f"https://example.com/{identifier}",
        identifier,
        SourceClassification.CANONICAL,
        enabled,
    )


def test_corpus_ingestion_fetches_only_enabled_manifest_urls_and_isolates_failures() -> None:
    fetcher = ManifestFetcher()
    repository = InMemoryDocumentRepository()
    pipeline = IngestionPipeline(
        fetcher,
        EmbeddingService(FakeClient(), model="fake", dimensions=3),
        repository,
    )
    manifest = CorpusManifest(
        1,
        "go-style",
        "Go",
        (_source("guide"), _source("disabled", False), _source("unavailable")),
    )

    run = CorpusIngestionService(pipeline).ingest(manifest)

    assert fetcher.urls == ["https://example.com/guide", "https://example.com/unavailable"]
    assert [outcome.status for outcome in run.outcomes] == [
        CorpusSourceStatus.SUCCEEDED,
        CorpusSourceStatus.SKIPPED,
        CorpusSourceStatus.FAILED,
    ]
    active = repository.active_document("https://example.com/guide")
    assert active is not None
    assert (active.corpus_id, active.manifest_source_id) == ("go-style", "guide")
    assert repository.count_active_sections() == 1
