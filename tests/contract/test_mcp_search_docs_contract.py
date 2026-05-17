import json
from pathlib import Path
from uuid import uuid4

from net2vec.domain.search import SearchResponse, SearchResult
from net2vec.mcp import server


class FakeSearchService:
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        return SearchResponse(query=query, results=(_result(),), no_match_reason=None)


def test_search_docs_tool_definition_matches_contract() -> None:
    contract = _contract()

    tool_definition = server.search_docs_tool_definition()

    assert tool_definition["name"] == contract["tool"]["name"]
    assert tool_definition["description"] == contract["tool"]["description"]
    assert tool_definition["input_schema"] == contract["tool"]["input_schema"]
    assert tool_definition["output_schema"] == contract["tool"]["output_schema"]


def test_search_docs_output_matches_contract_shape() -> None:
    contract = _contract()

    response = server.handle_search_docs(
        {"query": "mixed caps", "limit": 1},
        FakeSearchService(),
    )

    assert set(response) <= set(contract["tool"]["output_schema"]["properties"])
    assert set(response["results"][0]) == _required_result_fields()


def _contract() -> dict:
    path = Path("specs/001-docs-vector-ingestion/contracts/mcp-search-docs.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _required_result_fields() -> set[str]:
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
