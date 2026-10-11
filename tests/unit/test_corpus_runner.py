from types import SimpleNamespace
from uuid import uuid4

from net2vec.domain.corpus import (
    CorpusManifest,
    CorpusSource,
    CorpusSourceStatus,
    SourceClassification,
)
from net2vec.domain.documents import IngestionError, SourceDocument
from net2vec.ingestion.corpus import CorpusIngestionService


class FakeIngestor:
    def __init__(self) -> None:
        self.calls = []

    def ingest(self, url, provenance=None):  # noqa: ANN001, ANN201
        self.calls.append((url, provenance))
        if url.endswith("failed"):
            raise IngestionError("URL fetch failed with status 503")
        if url.endswith("secret"):
            raise RuntimeError("password=hunter2")
        document = SourceDocument(source_url=url, id=uuid4(), content_hash="hash")
        return SimpleNamespace(document=document, sections=(object(), object()))


def _source(identifier: str, suffix: str, enabled: bool = True) -> CorpusSource:
    return CorpusSource(
        identifier,
        f"https://example.com/{suffix}",
        identifier,
        SourceClassification.CANONICAL,
        enabled,
    )


def test_runner_preserves_order_and_reports_every_entry() -> None:
    ingestor = FakeIngestor()
    manifest = CorpusManifest(
        1,
        "go-style",
        "Go",
        (_source("one", "one"), _source("two", "two", False), _source("three", "failed")),
    )

    run = CorpusIngestionService(ingestor).ingest(manifest)

    assert tuple(outcome.source_id for outcome in run.outcomes) == ("one", "two", "three")
    assert tuple(outcome.status for outcome in run.outcomes) == (
        CorpusSourceStatus.SUCCEEDED,
        CorpusSourceStatus.SKIPPED,
        CorpusSourceStatus.FAILED,
    )
    assert (run.succeeded, run.skipped, run.failed) == (1, 1, 1)
    assert ingestor.calls[0][0] == "https://example.com/one"
    assert ingestor.calls[1][0] == "https://example.com/failed"


def test_runner_passes_stable_provenance_to_ingestor() -> None:
    ingestor = FakeIngestor()
    manifest = CorpusManifest(1, "go-style", "Go", (_source("guide", "guide"),))

    CorpusIngestionService(ingestor).ingest(manifest)

    provenance = ingestor.calls[0][1]
    values = (
        provenance.corpus_id,
        provenance.manifest_source_id,
        provenance.source_classification,
    )
    assert values == ("go-style", "guide", "canonical")


def test_runner_sanitizes_unexpected_exception_messages(caplog) -> None:  # noqa: ANN001
    ingestor = FakeIngestor()
    manifest = CorpusManifest(1, "go-style", "Go", (_source("secret", "secret"),))

    with caplog.at_level("DEBUG", logger="net2vec.ingestion.corpus"):
        run = CorpusIngestionService(ingestor).ingest(manifest)

    assert run.outcomes[0].message == "RuntimeError during source ingestion"
    assert "hunter2" not in run.outcomes[0].message
    assert "password=hunter2" in caplog.text
    assert "Traceback" in caplog.text


def test_runner_reports_each_outcome_as_it_completes() -> None:
    manifest = CorpusManifest(
        1,
        "go-style",
        "Go",
        (_source("one", "one"), _source("two", "failed")),
    )
    reported = []

    run = CorpusIngestionService(FakeIngestor()).ingest(manifest, reported.append)

    assert tuple(outcome.source_id for outcome in reported) == ("one", "two")
    assert tuple(reported) == run.outcomes
