"""MCP server adapter for documentation search."""

from __future__ import annotations

from typing import Any, Protocol

from net2vec.config.settings import Settings
from net2vec.domain.search import SearchQuery, SearchResponse, SearchResult
from net2vec.embeddings.client import OpenAIEmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.persistence.database import create_session_factory
from net2vec.persistence.repositories import SqlAlchemyDocumentRepository
from net2vec.search.service import SearchService

TOOL_NAME = "search_docs"
TOOL_DESCRIPTION = (
    "Search active ingested documentation chunks and return source-grounded excerpts plus "
    "full stored chunk text."
)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001
DEFAULT_PATH = "/mcp"


class SearchServicePort(Protocol):
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        """Search active documentation chunks."""


class MCPValidationError(ValueError):
    """Raised when MCP tool input is invalid."""


def search_docs_tool_definition() -> dict[str, Any]:
    return {
        "name": TOOL_NAME,
        "description": TOOL_DESCRIPTION,
        "input_schema": _input_schema(),
        "output_schema": _output_schema(),
    }


def handle_search_docs(payload: dict[str, Any], service: SearchServicePort) -> dict[str, Any]:
    query = _search_query(payload)
    response = service.search(query.query, query.limit)
    return _response_payload(response)


def create_mcp_server(search_service: SearchServicePort | None = None):
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(
        "net2vec",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        streamable_http_path=DEFAULT_PATH,
    )
    server.add_tool(
        _tool_handler(search_service),
        name=TOOL_NAME,
        description=TOOL_DESCRIPTION,
        structured_output=True,
    )
    return server


def main() -> None:
    create_mcp_server().run("streamable-http")


def _tool_handler(search_service: SearchServicePort | None):
    def search_docs(query: str, limit: int = 5) -> dict[str, Any]:
        return handle_search_docs({"query": query, "limit": limit}, _service(search_service))

    return search_docs


def _service(search_service: SearchServicePort | None) -> SearchServicePort:
    if search_service is not None:
        return search_service
    return _default_search_service()


def _default_search_service() -> SearchService:
    settings = Settings.from_env()
    session_factory = create_session_factory(settings.database_url)
    session = session_factory()
    return SearchService(_embedding_service(settings), SqlAlchemyDocumentRepository(session))


def _embedding_service(settings: Settings) -> EmbeddingService:
    return EmbeddingService(
        OpenAIEmbeddingClient(settings.openai_api_key),
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )


def _search_query(payload: dict[str, Any]) -> SearchQuery:
    try:
        _reject_unknown_fields(payload)
        return SearchQuery(query=_query(payload), limit=_limit(payload))
    except ValueError as exc:
        raise MCPValidationError(str(exc)) from exc


def _reject_unknown_fields(payload: dict[str, Any]) -> None:
    extra_fields = set(payload) - {"query", "limit"}
    if extra_fields:
        raise MCPValidationError("unexpected search_docs input fields")


def _query(payload: dict[str, Any]) -> str:
    value = payload.get("query", "")
    if not isinstance(value, str):
        raise MCPValidationError("query must contain text")
    return value


def _limit(payload: dict[str, Any]) -> int:
    return int(payload.get("limit", 5))


def _response_payload(response: SearchResponse) -> dict[str, Any]:
    return {
        "results": [_result_payload(result) for result in response.results],
        "no_match_reason": response.no_match_reason,
    }


def _result_payload(result: SearchResult) -> dict[str, Any]:
    return {
        "section_id": str(result.section_id),
        "document_id": str(result.document_id),
        "source_url": result.source_url,
        "title": result.title,
        "heading_path": list(result.heading_path),
        "excerpt": result.excerpt,
        "full_chunk_text": result.full_chunk_text,
        "rank": result.rank,
        "score": result.score,
    }


def _input_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["query"],
        "additionalProperties": False,
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "description": "Natural-language documentation search query.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "default": 5,
                "description": "Maximum number of results to return.",
            },
        },
    }


def _output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["results"],
        "additionalProperties": False,
        "properties": {
            "results": {"type": "array", "items": _result_schema()},
            "no_match_reason": {"type": "string"},
        },
    }


def _result_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": _required_result_fields(),
        "additionalProperties": False,
        "properties": _result_properties(),
    }


def _required_result_fields() -> list[str]:
    return [
        "section_id",
        "document_id",
        "source_url",
        "heading_path",
        "excerpt",
        "full_chunk_text",
        "rank",
        "score",
    ]


def _result_properties() -> dict[str, Any]:
    return {
        "section_id": {"type": "string"},
        "document_id": {"type": "string"},
        "source_url": {"type": "string"},
        "title": {"type": "string"},
        "heading_path": {"type": "array", "items": {"type": "string"}},
        "excerpt": {"type": "string"},
        "full_chunk_text": {"type": "string"},
        "rank": {"type": "integer"},
        "score": {"type": "number"},
    }


if __name__ == "__main__":
    main()
