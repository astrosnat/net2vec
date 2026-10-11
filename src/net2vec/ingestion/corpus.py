"""Curated corpus ingestion orchestration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from net2vec.domain.corpus import (
    CorpusIngestionRun,
    CorpusManifest,
    CorpusSource,
    CorpusSourceOutcome,
    CorpusSourceStatus,
)
from net2vec.domain.documents import DocumentProvenance, Net2VecError
from net2vec.ingestion.pipeline import IngestionResult

LOGGER = logging.getLogger(__name__)
OutcomeCallback = Callable[[CorpusSourceOutcome], None]


class SourceIngestor(Protocol):
    def ingest(
        self,
        url: str,
        provenance: DocumentProvenance | None = None,
    ) -> IngestionResult:
        """Ingest one exact source URL."""


class CorpusIngestionService:
    def __init__(self, ingestor: SourceIngestor) -> None:
        self.ingestor = ingestor

    def ingest(
        self,
        manifest: CorpusManifest,
        on_outcome: OutcomeCallback | None = None,
    ) -> CorpusIngestionRun:
        started_at = datetime.now(UTC)
        outcomes = tuple(self._ingest_sources(manifest, on_outcome))
        return CorpusIngestionRun(manifest.corpus_id, started_at, datetime.now(UTC), outcomes)

    def _ingest_sources(
        self,
        manifest: CorpusManifest,
        on_outcome: OutcomeCallback | None,
    ):  # noqa: ANN202
        for source in manifest.sources:
            outcome = self._ingest_source(manifest.corpus_id, source)
            if on_outcome is not None:
                on_outcome(outcome)
            yield outcome

    def _ingest_source(self, corpus_id: str, source: CorpusSource) -> CorpusSourceOutcome:
        if not source.enabled:
            return _skipped(source)
        return self._enabled_source(corpus_id, source)

    def _enabled_source(self, corpus_id: str, source: CorpusSource) -> CorpusSourceOutcome:
        try:
            result = self.ingestor.ingest(source.url, _provenance(corpus_id, source))
        except Exception as exc:  # noqa: BLE001 - source isolation is the service boundary
            _log_unexpected(source, exc)
            return _failed(source, exc)
        return _succeeded(source, result)


def _provenance(corpus_id: str, source: CorpusSource) -> DocumentProvenance:
    return DocumentProvenance(corpus_id, source.id, source.classification.value)


def _skipped(source: CorpusSource) -> CorpusSourceOutcome:
    return CorpusSourceOutcome(
        source.id,
        source.url,
        CorpusSourceStatus.SKIPPED,
        0,
        message="disabled in manifest",
    )


def _failed(source: CorpusSource, exc: Exception) -> CorpusSourceOutcome:
    return CorpusSourceOutcome(
        source.id,
        source.url,
        CorpusSourceStatus.FAILED,
        0,
        message=_safe_error(exc),
    )


def _safe_error(exc: Exception) -> str:
    if isinstance(exc, Net2VecError):
        return str(exc)
    return f"{type(exc).__name__} during source ingestion"


def _log_unexpected(source: CorpusSource, exc: Exception) -> None:
    if isinstance(exc, Net2VecError):
        return
    LOGGER.debug(
        "unexpected exception ingesting corpus source %s (%s)",
        source.id,
        source.url,
        exc_info=True,
    )


def _succeeded(source: CorpusSource, result: IngestionResult) -> CorpusSourceOutcome:
    return CorpusSourceOutcome(
        source.id,
        source.url,
        CorpusSourceStatus.SUCCEEDED,
        len(result.sections),
        document_id=result.document.id,
        content_hash=result.document.content_hash,
    )
