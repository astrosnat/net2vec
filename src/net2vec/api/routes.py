"""HTTP route handlers."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from net2vec.config.settings import Settings
from net2vec.domain.documents import IngestionError
from net2vec.domain.search import SearchResponse
from net2vec.embeddings.client import OpenAIEmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.fetcher import HttpFetcher
from net2vec.ingestion.pipeline import IngestionPipeline, IngestionResult
from net2vec.persistence.database import create_session_factory
from net2vec.persistence.repositories import SqlAlchemyDocumentRepository
from net2vec.search.service import SearchService


class SearchServicePort(Protocol):
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        """Search active documentation chunks."""


class IngestionPipelinePort(Protocol):
    def ingest(self, url: str) -> IngestionResult:
        """Ingest or refresh one exact documentation URL."""


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str


class IngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    source_url: str
    status: str
    chunks_indexed: int
    refreshed: bool
    message: str | None = None


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class SearchResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: UUID
    document_id: UUID
    source_url: str
    title: str | None = None
    heading_path: list[str]
    excerpt: str
    full_chunk_text: str
    rank: int
    score: float


class SearchResponseBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    results: list[SearchResultResponse]
    no_match_reason: str | None = None


def create_router(
    search_service: SearchServicePort | None = None,
    ingestion_pipeline: IngestionPipelinePort | None = None,
) -> APIRouter:
    router = APIRouter()

    @router.post("/ingest", response_model=IngestResponse, status_code=202)
    def ingest(request: IngestRequest):
        try:
            result = _ingest(request.url, ingestion_pipeline)
        except IngestionError as exc:
            return _ingest_error_response(exc)
        return _ingest_response(result)

    @router.post(
        "/search",
        response_model=SearchResponseBody,
        response_model_exclude_none=True,
    )
    def search(request: SearchRequest):
        try:
            response = _search(request, search_service)
        except ValueError as exc:
            return _error_response(400, "invalid_search_request", str(exc))
        return _search_response(response)

    return router


def _ingest(url: str, pipeline: IngestionPipelinePort | None) -> IngestionResult:
    if pipeline is not None:
        return pipeline.ingest(url)
    return _ingest_with_default_pipeline(url)


def _search(request: SearchRequest, service: SearchServicePort | None) -> SearchResponse:
    if service is not None:
        return service.search(request.query, request.limit)
    return _search_with_default_service(request)


def _ingest_with_default_pipeline(url: str) -> IngestionResult:
    settings = Settings.from_env()
    session_factory = create_session_factory(settings.database_url)
    session = session_factory()
    try:
        return _default_ingestion_pipeline(settings, session).ingest(url)
    finally:
        session.close()


def _search_with_default_service(request: SearchRequest) -> SearchResponse:
    settings = Settings.from_env()
    session_factory = create_session_factory(settings.database_url)
    session = session_factory()
    try:
        return _default_search_service(settings, session).search(request.query, request.limit)
    finally:
        session.close()


def _default_ingestion_pipeline(settings: Settings, session) -> IngestionPipeline:  # noqa: ANN001
    return IngestionPipeline(
        fetcher=HttpFetcher(),
        embedding_service=_embedding_service(settings),
        repository=SqlAlchemyDocumentRepository(session),
    )


def _default_search_service(settings: Settings, session) -> SearchService:  # noqa: ANN001
    return SearchService(_embedding_service(settings), SqlAlchemyDocumentRepository(session))


def _embedding_service(settings: Settings) -> EmbeddingService:
    return EmbeddingService(
        OpenAIEmbeddingClient(settings.openai_api_key),
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )


def _ingest_response(result: IngestionResult) -> IngestResponse:
    return IngestResponse(
        document_id=result.document.id,
        source_url=result.document.source_url,
        status=result.document.retrieval_status.value,
        chunks_indexed=len(result.sections),
        refreshed=False,
        message=None,
    )


def _search_response(response: SearchResponse) -> SearchResponseBody:
    return SearchResponseBody(
        query=response.query,
        results=[_search_result(result) for result in response.results],
        no_match_reason=response.no_match_reason,
    )


def _search_result(result) -> SearchResultResponse:  # noqa: ANN001
    return SearchResultResponse(
        section_id=result.section_id,
        document_id=result.document_id,
        source_url=result.source_url,
        title=result.title,
        heading_path=list(result.heading_path),
        excerpt=result.excerpt,
        full_chunk_text=result.full_chunk_text,
        rank=result.rank,
        score=result.score,
    )


def _ingest_error_response(exc: IngestionError) -> JSONResponse:
    status_code = 400 if _is_url_error(str(exc)) else 502
    return _error_response(status_code, "ingestion_failed", str(exc))


def _is_url_error(message: str) -> bool:
    return message.startswith("URL must") or message.startswith("URL fragments")


def _error_response(status_code: int, error: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "detail": detail})
