from uuid import uuid4

from net2vec.domain.chunks import DocumentSection
from net2vec.domain.documents import SourceDocument
from net2vec.persistence.repositories import InMemoryDocumentRepository


def _section(document_id, text: str) -> DocumentSection:
    return DocumentSection(
        document_id=document_id,
        chunk_index=0,
        heading_path=("Names",),
        excerpt=text,
        full_chunk_text=text,
        token_count=1,
        content_hash=text,
        embedding_model="fake",
        embedding_dimensions=3,
        embedding=(1.0, 0.0, 0.0),
    )


def test_refresh_replaces_active_sections_for_url() -> None:
    repo = InMemoryDocumentRepository()
    first = SourceDocument(source_url="https://go.dev/doc/effective_go", id=uuid4())
    second = SourceDocument(source_url="https://go.dev/doc/effective_go", id=uuid4())

    repo.replace_active(first, [_section(first.id, "old")])
    repo.replace_active(second, [_section(second.id, "new")])

    assert repo.active_document("https://go.dev/doc/effective_go") == second
    assert [section.full_chunk_text for section in repo.active_sections(second.id)] == ["new"]
    assert repo.active_sections(first.id) == []


def test_search_match_preserves_manifest_provenance() -> None:
    repo = InMemoryDocumentRepository()
    document = SourceDocument(
        source_url="https://go.dev/doc/effective_go",
        resolved_url="https://go.dev/doc/effective_go",
        corpus_id="go-style",
        manifest_source_id="effective-go",
        source_classification="baseline",
    )
    repo.replace_active(document, [_section(document.id, "names")])

    match = repo.search_active_sections((1.0, 0.0, 0.0), limit=1)[0]

    assert match.corpus_id == "go-style"
    assert match.manifest_source_id == "effective-go"
    assert match.source_classification == "baseline"
    assert match.resolved_url == "https://go.dev/doc/effective_go"
