"""Search ranking helpers."""

from __future__ import annotations

from net2vec.domain.search import SearchMatch, SearchResult

MINIMUM_SCORE = 0.0


def rank_matches(matches: list[SearchMatch]) -> tuple[SearchResult, ...]:
    scored = _scored_matches(matches)
    return tuple(
        _search_result(match, rank, score)
        for rank, (match, score) in enumerate(scored, start=1)
    )


def normalize_score(distance: float) -> float:
    return min(1.0, max(0.0, 1.0 - distance))


def _scored_matches(matches: list[SearchMatch]) -> list[tuple[SearchMatch, float]]:
    return [
        (match, score)
        for match in matches
        if (score := normalize_score(match.distance)) > MINIMUM_SCORE
    ]


def _search_result(match: SearchMatch, rank: int, score: float) -> SearchResult:
    return SearchResult(
        section_id=match.section_id,
        document_id=match.document_id,
        source_url=match.source_url,
        title=match.title,
        heading_path=match.heading_path,
        excerpt=match.excerpt,
        full_chunk_text=match.full_chunk_text,
        rank=rank,
        score=score,
    )
