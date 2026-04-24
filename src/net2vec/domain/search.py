"""Search domain models."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SearchQuery:
    query: str
    limit: int = 5

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must contain text")
        if not 1 <= self.limit <= 20:
            raise ValueError("limit must be between 1 and 20")


@dataclass(frozen=True)
class SearchResult:
    section_id: UUID
    document_id: UUID
    source_url: str
    heading_path: tuple[str, ...]
    excerpt: str
    full_chunk_text: str
    rank: int
    score: float
    title: str | None = None
