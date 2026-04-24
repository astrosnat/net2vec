"""Ingestion orchestration."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

from net2vec.domain.chunks import DocumentSection
from net2vec.domain.documents import SourceDocument
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.chunker import ChunkDraft, build_chunks
from net2vec.ingestion.extractor import extract_page
from net2vec.ingestion.fetcher import validate_exact_url
from net2vec.persistence.repositories import DocumentRepository

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestionResult:
    document: SourceDocument
    sections: tuple[DocumentSection, ...]


class IngestionPipeline:
    def __init__(
        self,
        fetcher,
        embedding_service: EmbeddingService,
        repository: DocumentRepository,
    ) -> None:
        self.fetcher = fetcher
        self.embedding_service = embedding_service
        self.repository = repository

    def ingest(self, url: str) -> IngestionResult:
        exact_url = validate_exact_url(url)
        fetched = self.fetcher.fetch(exact_url)
        page = extract_page(fetched.html)
        drafts = build_chunks(page.blocks, source_url=exact_url)
        embeddings = self.embedding_service.embed_texts([draft.full_chunk_text for draft in drafts])
        document = _document(exact_url, page.title, fetched.html, fetched.status_code)
        sections = _sections(document, drafts, embeddings, self.embedding_service)
        self.repository.replace_active(document, sections)
        LOGGER.info(
            "ingested documentation page",
            extra={"url": exact_url, "chunks": len(sections)},
        )
        return IngestionResult(document=document, sections=tuple(sections))


def _document(url: str, title: str | None, html: str, status_code: int | None) -> SourceDocument:
    document = SourceDocument(source_url=url)
    document.mark_succeeded(title=title, content_hash=_hash(html), http_status=status_code)
    return document


def _sections(
    document: SourceDocument,
    drafts: list[ChunkDraft],
    embeddings: list[tuple[float, ...]],
    service: EmbeddingService,
) -> list[DocumentSection]:
    return [
        _section(document, draft, vector, service)
        for draft, vector in zip(drafts, embeddings, strict=True)
    ]


def _section(
    document: SourceDocument,
    draft: ChunkDraft,
    vector: tuple[float, ...],
    service: EmbeddingService,
) -> DocumentSection:
    return DocumentSection(
        document_id=document.id,
        chunk_index=draft.chunk_index,
        heading_path=draft.heading_path,
        heading_text=draft.heading_text,
        excerpt=draft.excerpt,
        full_chunk_text=draft.full_chunk_text,
        token_count=draft.token_count,
        content_hash=draft.content_hash,
        embedding_model=service.model,
        embedding_dimensions=service.dimensions,
        embedding=vector,
    )


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
