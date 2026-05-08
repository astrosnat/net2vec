from uuid import uuid4

import pytest

from net2vec.domain.chunks import DocumentSection
from net2vec.domain.documents import SourceDocument
from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.persistence.repositories import InMemoryDocumentRepository
from net2vec.search.service import SearchService


class FakeClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [_vector_for(text) for text in texts]


def test_search_query_rejects_blank_query_and_invalid_limit() -> None:
    service = _service(InMemoryDocumentRepository())

    with pytest.raises(ValueError, match="query must contain text"):
        service.search("   ", limit=5)

    with pytest.raises(ValueError, match="limit must be between 1 and 20"):
        service.search("mixed caps", limit=21)


def test_search_ranks_results_and_filters_inactive_sections() -> None:
    repo = InMemoryDocumentRepository()
    active = SourceDocument(source_url="https://go.dev/doc/effective_go", id=uuid4())
    inactive = SourceDocument(source_url="https://go.dev/doc/effective_go", id=uuid4())
    repo.replace_active(inactive, [_section(inactive.id, "old mixed caps", (1.0, 0.0, 0.0))])
    repo.replace_active(
        active,
        [
            _section(active.id, "initialisms stay consistent", (0.0, 1.0, 0.0)),
            _section(active.id, "mixed caps are preferred", (1.0, 0.0, 0.0)),
        ],
    )

    response = _service(repo).search("mixed caps", limit=5)

    assert response.no_match_reason is None
    assert [result.rank for result in response.results] == [1]
    assert response.results[0].full_chunk_text == "mixed caps are preferred"
    assert response.results[0].source_url == "https://go.dev/doc/effective_go"
    assert response.results[0].score == 1.0


def test_search_returns_no_match_for_unrelated_query() -> None:
    repo = InMemoryDocumentRepository()
    document = SourceDocument(source_url="https://go.dev/doc/effective_go")
    section = _section(document.id, "mixed caps are preferred", (1.0, 0.0, 0.0))
    repo.replace_active(document, [section])

    response = _service(repo).search("unrelated topic", limit=5)

    assert response.results == ()
    assert response.no_match_reason == "no matching active chunks"


def test_search_returns_empty_corpus_message() -> None:
    response = _service(InMemoryDocumentRepository()).search("mixed caps", limit=5)

    assert response.results == ()
    assert response.no_match_reason == "empty corpus"


def _service(repo: InMemoryDocumentRepository) -> SearchService:
    return SearchService(EmbeddingService(FakeClient(), model="fake", dimensions=3), repo)


def _section(document_id, text: str, embedding: tuple[float, ...]) -> DocumentSection:
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
        embedding=embedding,
    )


def _vector_for(text: str) -> list[float]:
    lowered = text.lower()
    if "mixed" in lowered:
        return [1.0, 0.0, 0.0]
    if "initialism" in lowered:
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]
