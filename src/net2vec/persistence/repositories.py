"""Document repository interfaces and implementations."""

from __future__ import annotations

import math
from typing import Protocol
from uuid import UUID

from net2vec.domain.chunks import DocumentSection
from net2vec.domain.documents import SourceDocument
from net2vec.domain.search import SearchMatch


class DocumentRepository(Protocol):
    def replace_active(self, document: SourceDocument, sections: list[DocumentSection]) -> None:
        """Replace active content for the document source URL."""


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self.documents: dict[UUID, SourceDocument] = {}
        self.sections: dict[UUID, list[DocumentSection]] = {}

    def replace_active(self, document: SourceDocument, sections: list[DocumentSection]) -> None:
        self._deactivate_url(document.source_url)
        self.documents[document.id] = document
        self.sections[document.id] = sections

    def active_document(self, source_url: str) -> SourceDocument | None:
        for document in self.documents.values():
            if _active_source(document, source_url):
                return document
        return None

    def active_sections(self, document_id: UUID) -> list[DocumentSection]:
        return [section for section in self.sections.get(document_id, []) if section.active]

    def count_active_sections(self) -> int:
        return sum(len(self.active_sections(document.id)) for document in self._active_documents())

    def search_active_sections(
        self,
        query_embedding: tuple[float, ...],
        limit: int,
    ) -> list[SearchMatch]:
        matches = self._search_matches(query_embedding)
        return sorted(matches, key=lambda match: match.distance)[:limit]

    def _deactivate_url(self, source_url: str) -> None:
        for document in self.documents.values():
            if document.source_url == source_url:
                document.active = False
                self._deactivate_sections(document.id)

    def _deactivate_sections(self, document_id: UUID) -> None:
        self.sections[document_id] = [
            _inactive_section(section) for section in self.sections.get(document_id, [])
        ]

    def _active_documents(self) -> list[SourceDocument]:
        return [document for document in self.documents.values() if document.active]

    def _search_matches(self, query_embedding: tuple[float, ...]) -> list[SearchMatch]:
        return [
            _search_match(document, section, query_embedding)
            for document in self._active_documents()
            for section in self.active_sections(document.id)
        ]


class SqlAlchemyDocumentRepository:
    def __init__(self, session) -> None:  # noqa: ANN001
        self.session = session

    def replace_active(self, document: SourceDocument, sections: list[DocumentSection]) -> None:
        from net2vec.persistence.models import DocumentSectionRecord, SourceDocumentRecord

        self._deactivate_existing(document.source_url)
        record = _document_record(SourceDocumentRecord, document)
        self.session.add(record)
        self.session.flush()
        self.session.add_all(_section_records(DocumentSectionRecord, sections))
        self.session.commit()

    def count_active_sections(self) -> int:
        from net2vec.persistence.models import DocumentSectionRecord, SourceDocumentRecord

        return (
            self.session.query(DocumentSectionRecord)
            .join(SourceDocumentRecord)
            .filter(DocumentSectionRecord.active.is_(True), SourceDocumentRecord.active.is_(True))
            .count()
        )

    def search_active_sections(
        self,
        query_embedding: tuple[float, ...],
        limit: int,
    ) -> list[SearchMatch]:
        from net2vec.persistence.models import DocumentSectionRecord, SourceDocumentRecord

        distance = DocumentSectionRecord.embedding.cosine_distance(list(query_embedding))
        rows = (
            self.session.query(DocumentSectionRecord, SourceDocumentRecord, distance)
            .join(SourceDocumentRecord)
            .filter(DocumentSectionRecord.active.is_(True), SourceDocumentRecord.active.is_(True))
            .order_by(distance)
            .limit(limit)
            .all()
        )
        return [
            _record_search_match(section, document, float(score))
            for section, document, score in rows
        ]

    def _deactivate_existing(self, source_url: str) -> None:
        from net2vec.persistence.models import DocumentSectionRecord, SourceDocumentRecord

        documents = self._active_records(SourceDocumentRecord, source_url)
        document_ids = [document.id for document in documents]
        self._deactivate_records(documents)
        self._deactivate_records(self._section_records_for(DocumentSectionRecord, document_ids))

    def _active_records(self, model, source_url: str):  # noqa: ANN001, ANN201
        return self.session.query(model).filter_by(source_url=source_url, active=True).all()

    def _section_records_for(self, model, document_ids: list[UUID]):  # noqa: ANN001, ANN201
        return self.session.query(model).filter(model.document_id.in_(document_ids)).all()

    def _deactivate_records(self, records: list) -> None:
        for record in records:
            record.active = False


def _inactive_section(section: DocumentSection) -> DocumentSection:
    return DocumentSection(
        document_id=section.document_id,
        chunk_index=section.chunk_index,
        heading_path=section.heading_path,
        excerpt=section.excerpt,
        full_chunk_text=section.full_chunk_text,
        token_count=section.token_count,
        content_hash=section.content_hash,
        embedding_model=section.embedding_model,
        embedding_dimensions=section.embedding_dimensions,
        embedding=section.embedding,
        heading_text=section.heading_text,
        id=section.id,
        active=False,
        created_at=section.created_at,
    )


def _active_source(document: SourceDocument, source_url: str) -> bool:
    return document.source_url == source_url and document.active


def _document_record(record_type, document: SourceDocument):  # noqa: ANN001, ANN201
    return record_type(
        id=document.id,
        source_url=document.source_url,
        title=document.title,
        retrieval_status=document.retrieval_status.value,
        http_status=document.http_status,
        content_hash=document.content_hash,
        active=document.active,
        ingested_at=document.ingested_at,
        refreshed_at=document.refreshed_at,
        error_message=document.error_message,
    )


def _section_records(record_type, sections: list[DocumentSection]) -> list:  # noqa: ANN001
    return [_section_record(record_type, section) for section in sections]


def _section_record(record_type, section: DocumentSection):  # noqa: ANN001, ANN201
    return record_type(
        id=section.id,
        document_id=section.document_id,
        chunk_index=section.chunk_index,
        heading_path=list(section.heading_path),
        heading_text=section.heading_text,
        excerpt=section.excerpt,
        full_chunk_text=section.full_chunk_text,
        token_count=section.token_count,
        content_hash=section.content_hash,
        embedding_model=section.embedding_model,
        embedding_dimensions=section.embedding_dimensions,
        embedding=list(section.embedding),
        active=section.active,
        created_at=section.created_at,
    )


def _search_match(
    document: SourceDocument,
    section: DocumentSection,
    query_embedding: tuple[float, ...],
) -> SearchMatch:
    return SearchMatch(
        section_id=section.id,
        document_id=document.id,
        source_url=document.source_url,
        title=document.title,
        heading_path=section.heading_path,
        excerpt=section.excerpt,
        full_chunk_text=section.full_chunk_text,
        distance=_cosine_distance(query_embedding, section.embedding),
    )


def _record_search_match(section, document, distance: float) -> SearchMatch:  # noqa: ANN001
    return SearchMatch(
        section_id=section.id,
        document_id=document.id,
        source_url=document.source_url,
        title=document.title,
        heading_path=tuple(section.heading_path),
        excerpt=section.excerpt,
        full_chunk_text=section.full_chunk_text,
        distance=distance,
    )


def _cosine_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    denominator = _magnitude(left) * _magnitude(right)
    if denominator == 0:
        return 1.0
    return 1.0 - (_dot(left, right) / denominator)


def _dot(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    pairs = zip(left, right, strict=True)
    return sum(left_value * right_value for left_value, right_value in pairs)


def _magnitude(vector: tuple[float, ...]) -> float:
    return math.sqrt(sum(value * value for value in vector))
