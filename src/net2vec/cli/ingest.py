"""Ingest one exact documentation URL."""

from __future__ import annotations

from net2vec.config.settings import Settings
from net2vec.embeddings.client import OpenAIEmbeddingClient
from net2vec.embeddings.service import EmbeddingService
from net2vec.ingestion.fetcher import HttpFetcher
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.database import create_session_factory
from net2vec.persistence.repositories import SqlAlchemyDocumentRepository


def ingest_url(url: str) -> int:
    settings = Settings.from_env()
    session_factory = create_session_factory(settings.database_url)
    session = session_factory()
    try:
        result = _ingest_with_session(url, settings, session)
        print(f"ingested {result.document.source_url}: {len(result.sections)} chunks")
    finally:
        session.close()
    return 0


def _ingest_with_session(url: str, settings: Settings, session):
    pipeline = IngestionPipeline(
        fetcher=HttpFetcher(),
        embedding_service=EmbeddingService(
            OpenAIEmbeddingClient(settings.openai_api_key),
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        ),
        repository=SqlAlchemyDocumentRepository(session),
    )
    return pipeline.ingest(url)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest one exact documentation URL")
    parser.add_argument("url")
    args = parser.parse_args()
    raise SystemExit(ingest_url(args.url))


if __name__ == "__main__":
    main()
