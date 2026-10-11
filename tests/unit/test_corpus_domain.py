from datetime import UTC, datetime
from uuid import uuid4

import pytest

from net2vec.domain.corpus import (
    CorpusIngestionRun,
    CorpusManifest,
    CorpusSource,
    CorpusSourceOutcome,
    CorpusSourceStatus,
    SourceClassification,
)
from net2vec.domain.documents import SourceDocument


def _source(**overrides) -> CorpusSource:
    values = {
        "id": "google-go-guide",
        "url": "https://google.github.io/styleguide/go/guide",
        "title": "Google Go Style Guide",
        "classification": SourceClassification.CANONICAL,
        "enabled": True,
    }
    values.update(overrides)
    return CorpusSource(**values)


def test_manifest_requires_unique_source_ids_and_urls() -> None:
    first = _source()
    duplicate_id = _source(url="https://go.dev/doc/effective_go")
    duplicate_url = _source(id="effective-go")

    with pytest.raises(ValueError, match="duplicate source id"):
        CorpusManifest(
            schema_version=1,
            corpus_id="go-style",
            title="Go",
            sources=(first, duplicate_id),
        )
    with pytest.raises(ValueError, match="duplicate source URL"):
        CorpusManifest(
            schema_version=1,
            corpus_id="go-style",
            title="Go",
            sources=(first, duplicate_url),
        )


def test_manifest_requires_supported_version_and_enabled_source() -> None:
    disabled = _source(enabled=False)

    with pytest.raises(ValueError, match="schema version"):
        CorpusManifest(schema_version=2, corpus_id="go-style", title="Go", sources=(disabled,))
    with pytest.raises(ValueError, match="enabled source"):
        CorpusManifest(schema_version=1, corpus_id="go-style", title="Go", sources=(disabled,))


@pytest.mark.parametrize("identifier", ["Go-Style", "go_style", "-go-style", "go-style-"])
def test_corpus_identifiers_use_lowercase_hyphenated_form(identifier: str) -> None:
    with pytest.raises(ValueError, match="identifier"):
        CorpusManifest(schema_version=1, corpus_id=identifier, title="Go", sources=(_source(),))


def test_source_rejects_unsupported_classification_and_non_https_url() -> None:
    with pytest.raises(ValueError, match="classification"):
        _source(classification="unknown")
    with pytest.raises(ValueError, match="HTTPS"):
        _source(url="http://example.com/guide")


def test_run_derives_terminal_outcome_counts() -> None:
    now = datetime.now(UTC)
    outcomes = (
        CorpusSourceOutcome("one", "https://example.com/one", CorpusSourceStatus.SUCCEEDED, 2),
        CorpusSourceOutcome("two", "https://example.com/two", CorpusSourceStatus.FAILED, 0),
        CorpusSourceOutcome("three", "https://example.com/three", CorpusSourceStatus.SKIPPED, 0),
    )

    run = CorpusIngestionRun("go-style", now, now, outcomes)

    assert (run.succeeded, run.failed, run.skipped) == (1, 1, 1)


def test_failed_and_skipped_outcomes_cannot_report_sections() -> None:
    with pytest.raises(ValueError, match="zero sections"):
        CorpusSourceOutcome("one", "https://example.com", CorpusSourceStatus.FAILED, 1)


def test_document_provenance_is_all_present_or_all_absent() -> None:
    legacy = SourceDocument(source_url="https://go.dev/doc/effective_go")
    manifest_document = SourceDocument(
        source_url="https://go.dev/doc/effective_go",
        corpus_id="go-style",
        manifest_source_id="effective-go",
        source_classification="baseline",
        resolved_url="https://go.dev/doc/effective_go",
    )

    assert legacy.corpus_id is None
    assert manifest_document.manifest_source_id == "effective-go"
    with pytest.raises(ValueError, match="provenance"):
        SourceDocument(
            source_url="https://go.dev/doc/effective_go",
            corpus_id="go-style",
        )


def test_outcome_rejects_negative_section_count() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        CorpusSourceOutcome(
            "one",
            "https://example.com",
            CorpusSourceStatus.SUCCEEDED,
            -1,
            document_id=uuid4(),
        )
