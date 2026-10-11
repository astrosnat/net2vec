"""Ingest every enabled source in a validated corpus manifest."""

from __future__ import annotations

import sys
from pathlib import Path

from net2vec.config.settings import Settings
from net2vec.domain.corpus import CorpusIngestionRun, CorpusSourceOutcome
from net2vec.embeddings.factory import EmbeddingConfigurationError, create_embedding_service
from net2vec.ingestion.corpus import CorpusIngestionService
from net2vec.ingestion.fetcher import HttpFetcher
from net2vec.ingestion.manifest import DEFAULT_MANIFEST_PATH, ManifestValidationError, load_manifest
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.database import create_session_factory
from net2vec.persistence.repositories import SqlAlchemyDocumentRepository


def ingest_corpus(manifest_path: str | Path = DEFAULT_MANIFEST_PATH) -> int:
    try:
        manifest = load_manifest(manifest_path)
        run = _run_manifest(manifest)
    except (ManifestValidationError, EmbeddingConfigurationError) as exc:
        print(f"manifest validation error: {exc}", file=sys.stderr)
        return 2
    _print_run(run)
    return 1 if run.failed else 0


def _run_manifest(manifest) -> CorpusIngestionRun:  # noqa: ANN001
    settings = Settings.from_env()
    session = create_session_factory(settings.database_url)()
    try:
        pipeline = IngestionPipeline(
            fetcher=HttpFetcher(),
            embedding_service=create_embedding_service(settings),
            repository=SqlAlchemyDocumentRepository(session),
        )
        return CorpusIngestionService(pipeline).ingest(manifest)
    finally:
        session.close()


def _print_run(run: CorpusIngestionRun) -> None:
    for outcome in run.outcomes:
        print(_outcome_line(outcome))
    print(
        f"corpus {run.corpus_id}: {run.succeeded} succeeded, "
        f"{run.failed} failed, {run.skipped} skipped",
    )


def _outcome_line(outcome: CorpusSourceOutcome) -> str:
    detail = _outcome_detail(outcome)
    return f"[{outcome.status.value}] {outcome.source_id}: {detail}"


def _outcome_detail(outcome: CorpusSourceOutcome) -> str:
    if outcome.message:
        return outcome.message
    return f"{outcome.sections_indexed} sections"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a curated documentation corpus")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH))
    args = parser.parse_args()
    raise SystemExit(ingest_corpus(args.manifest))


if __name__ == "__main__":
    main()
