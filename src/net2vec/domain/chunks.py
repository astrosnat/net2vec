"""Chunk domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DocumentSection:
    document_id: UUID
    chunk_index: int
    heading_path: tuple[str, ...]
    excerpt: str
    full_chunk_text: str
    token_count: int
    content_hash: str
    embedding_model: str
    embedding_dimensions: int
    embedding: tuple[float, ...]
    heading_text: str | None = None
    id: UUID = field(default_factory=uuid4)
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
