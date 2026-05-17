from uuid import uuid4

import pytest

from net2vec.domain.search import SearchResponse, SearchResult
from net2vec.mcp import server


class EmptySearchService:
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        return SearchResponse(query=query, results=(), no_match_reason="empty corpus")


class ResultSearchService:
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        return SearchResponse(query=query, results=(_result(),), no_match_reason=None)


def test_search_docs_returns_clear_no_match_response() -> None:
    response = server.handle_search_docs(
        {"query": "mixed caps", "limit": 3},
        EmptySearchService(),
    )

    assert response == {"results": [], "no_match_reason": "empty corpus"}


def test_search_docs_rejects_blank_query() -> None:
    with pytest.raises(server.MCPValidationError, match="query must contain text"):
        server.handle_search_docs({"query": "   ", "limit": 3}, EmptySearchService())


def test_search_docs_rejects_invalid_limit() -> None:
    with pytest.raises(server.MCPValidationError, match="limit must be between 1 and 20"):
        server.handle_search_docs({"query": "mixed caps", "limit": 21}, EmptySearchService())


def test_search_docs_includes_source_grounding_fields() -> None:
    response = server.handle_search_docs(
        {"query": "mixed caps", "limit": 1},
        ResultSearchService(),
    )

    assert response["no_match_reason"] is None
    assert response["results"][0]["source_url"] == "https://go.dev/doc/effective_go"
    assert response["results"][0]["heading_path"] == ["Names"]
    assert response["results"][0]["excerpt"] == "MixedCaps are preferred."
    assert response["results"][0]["full_chunk_text"] == "MixedCaps are preferred in Go names."
    assert response["results"][0]["rank"] == 1
    assert response["results"][0]["score"] == 0.99


def _result() -> SearchResult:
    return SearchResult(
        section_id=uuid4(),
        document_id=uuid4(),
        source_url="https://go.dev/doc/effective_go",
        title="Effective Go",
        heading_path=("Names",),
        excerpt="MixedCaps are preferred.",
        full_chunk_text="MixedCaps are preferred in Go names.",
        rank=1,
        score=0.99,
    )
