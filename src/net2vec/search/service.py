"""Semantic search orchestration."""

from __future__ import annotations

from typing import Protocol

from net2vec.domain.search import SearchMatch, SearchQuery, SearchResponse
from net2vec.embeddings.service import EmbeddingService
from net2vec.search.ranking import rank_matches


class SearchRepository(Protocol):
    def count_active_sections(self) -> int:
        """Return active searchable section count."""

    def search_active_sections(
        self,
        query_embedding: tuple[float, ...],
        limit: int,
    ) -> list[SearchMatch]:
        """Return active sections ordered by vector distance."""


class SearchService:
    def __init__(self, embedding_service: EmbeddingService, repository: SearchRepository) -> None:
        self.embedding_service = embedding_service
        self.repository = repository

    def search(self, query: str, limit: int = 5) -> SearchResponse:
        search_query = SearchQuery(query=query, limit=limit)
        if self.repository.count_active_sections() == 0:
            return _empty_response(search_query, "empty corpus")
        return self._search_active_corpus(search_query)

    def _search_active_corpus(self, search_query: SearchQuery) -> SearchResponse:
        embedding = self.embedding_service.embed_query(search_query.query)
        matches = self.repository.search_active_sections(embedding, search_query.limit)
        return _ranked_response(search_query, matches)


def _ranked_response(search_query: SearchQuery, matches: list[SearchMatch]) -> SearchResponse:
    results = rank_matches(matches)
    reason = None if results else "no matching active chunks"
    return SearchResponse(query=search_query.query, results=results, no_match_reason=reason)


def _empty_response(search_query: SearchQuery, reason: str) -> SearchResponse:
    return SearchResponse(query=search_query.query, results=(), no_match_reason=reason)
