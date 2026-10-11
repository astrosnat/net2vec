"""Domain models for curated documentation corpora."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from urllib.parse import urlparse
from uuid import UUID

SUPPORTED_MANIFEST_VERSION = 1
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SourceClassification(StrEnum):
    OVERVIEW = "overview"
    CANONICAL = "canonical"
    NORMATIVE = "normative"
    BEST_PRACTICE = "best-practice"
    BASELINE = "baseline"
    REVIEW = "review"
    TESTING = "testing"


class CorpusSourceStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class CorpusSource:
    id: str
    url: str
    title: str
    classification: SourceClassification
    enabled: bool

    def __post_init__(self) -> None:
        _validate_identifier(self.id, "source identifier")
        _validate_https_url(self.url)
        _require_text(self.title, "source title")
        _validate_classification(self.classification)


@dataclass(frozen=True)
class CorpusManifest:
    schema_version: int
    corpus_id: str
    title: str
    sources: tuple[CorpusSource, ...]

    def __post_init__(self) -> None:
        _validate_schema_version(self.schema_version)
        _validate_identifier(self.corpus_id, "corpus identifier")
        _require_text(self.title, "corpus title")
        _require_sources(self.sources)
        _require_enabled_source(self.sources)
        _require_unique_source_ids(self.sources)
        _require_unique_source_urls(self.sources)


@dataclass(frozen=True)
class CorpusSourceOutcome:
    source_id: str
    source_url: str
    status: CorpusSourceStatus
    sections_indexed: int
    document_id: UUID | None = None
    content_hash: str | None = None
    message: str | None = None

    def __post_init__(self) -> None:
        _validate_identifier(self.source_id, "source identifier")
        _validate_https_url(self.source_url)
        _require_non_negative(self.sections_indexed)
        _require_empty_unsuccessful_count(self.status, self.sections_indexed)


@dataclass(frozen=True)
class CorpusIngestionRun:
    corpus_id: str
    started_at: datetime
    completed_at: datetime
    outcomes: tuple[CorpusSourceOutcome, ...]

    def __post_init__(self) -> None:
        _validate_identifier(self.corpus_id, "corpus identifier")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")

    @property
    def succeeded(self) -> int:
        return _count_status(self.outcomes, CorpusSourceStatus.SUCCEEDED)

    @property
    def failed(self) -> int:
        return _count_status(self.outcomes, CorpusSourceStatus.FAILED)

    @property
    def skipped(self) -> int:
        return _count_status(self.outcomes, CorpusSourceStatus.SKIPPED)


def _validate_identifier(value: str, label: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(f"{label} must use lowercase hyphenated form")


def _validate_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("source URL must be an absolute HTTPS URL")


def _require_text(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must contain text")


def _validate_classification(value: SourceClassification) -> None:
    if not isinstance(value, SourceClassification):
        raise ValueError("unsupported source classification")


def _validate_schema_version(version: int) -> None:
    if version != SUPPORTED_MANIFEST_VERSION:
        raise ValueError(f"unsupported manifest schema version: {version}")


def _require_sources(sources: tuple[CorpusSource, ...]) -> None:
    if not sources:
        raise ValueError("manifest must contain at least one source")


def _require_enabled_source(sources: tuple[CorpusSource, ...]) -> None:
    if not any(source.enabled for source in sources):
        raise ValueError("manifest must contain at least one enabled source")


def _require_unique_source_ids(sources: tuple[CorpusSource, ...]) -> None:
    identifiers = [source.id for source in sources]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate source id in manifest")


def _require_unique_source_urls(sources: tuple[CorpusSource, ...]) -> None:
    urls = [_normalized_url(source.url) for source in sources]
    if len(urls) != len(set(urls)):
        raise ValueError("duplicate source URL in manifest")


def _normalized_url(url: str) -> str:
    return url.rstrip("/")


def _require_non_negative(value: int) -> None:
    if value < 0:
        raise ValueError("sections_indexed must be non-negative")


def _require_empty_unsuccessful_count(status: CorpusSourceStatus, count: int) -> None:
    if status != CorpusSourceStatus.SUCCEEDED and count:
        raise ValueError("failed and skipped outcomes must report zero sections")


def _count_status(
    outcomes: tuple[CorpusSourceOutcome, ...],
    status: CorpusSourceStatus,
) -> int:
    return sum(outcome.status == status for outcome in outcomes)
