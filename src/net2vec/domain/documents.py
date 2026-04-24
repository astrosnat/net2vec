"""Document domain models and errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class RetrievalStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Net2VecError(Exception):
    """Base application error."""


class IngestionError(Net2VecError):
    """Raised when ingestion cannot continue."""


@dataclass
class SourceDocument:
    source_url: str
    title: str | None = None
    id: UUID = field(default_factory=uuid4)
    retrieval_status: RetrievalStatus = RetrievalStatus.PENDING
    http_status: int | None = None
    content_hash: str | None = None
    active: bool = True
    ingested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    refreshed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_message: str | None = None

    def mark_succeeded(self, title: str | None, content_hash: str, http_status: int | None) -> None:
        self.title = title
        self.content_hash = content_hash
        self.http_status = http_status
        self.retrieval_status = RetrievalStatus.SUCCEEDED
        self.refreshed_at = datetime.now(UTC)
        self.error_message = None

    def mark_failed(self, message: str, http_status: int | None = None) -> None:
        self.http_status = http_status
        self.error_message = message
        self.retrieval_status = RetrievalStatus.FAILED
        self.refreshed_at = datetime.now(UTC)
