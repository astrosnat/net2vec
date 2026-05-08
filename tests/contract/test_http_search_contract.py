from uuid import uuid4

from fastapi.testclient import TestClient

from net2vec.api.app import create_app
from net2vec.domain.search import SearchResponse, SearchResult


class FakeSearchService:
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        return SearchResponse(query=query, results=(_result(),), no_match_reason=None)


def test_search_response_matches_openapi_contract_shape() -> None:
    contract = _openapi_contract()
    client = TestClient(create_app(search_service=FakeSearchService()))

    response = client.post("/search", json={"query": "mixed caps", "limit": 1})

    assert "/search:" in contract
    assert "SearchResult:" in contract
    assert response.status_code == 200
    assert set(response.json()) == {"query", "results"}
    assert set(response.json()["results"][0]) == _search_result_fields()


def test_search_validation_error_matches_contract_shape() -> None:
    client = TestClient(create_app(search_service=FakeSearchService()))

    response = client.post("/search", json={"query": "mixed caps", "limit": 21})

    assert response.status_code == 400
    assert set(response.json()) == {"error", "detail"}


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


def _search_result_fields() -> set[str]:
    return {
        "section_id",
        "document_id",
        "source_url",
        "title",
        "heading_path",
        "excerpt",
        "full_chunk_text",
        "rank",
        "score",
    }


def _openapi_contract() -> str:
    with open("specs/001-docs-vector-ingestion/contracts/openapi.yaml", encoding="utf-8") as file:
        return file.read()
