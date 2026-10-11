"""Ingest every enabled source in a validated corpus manifest."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from net2vec.config.settings import Settings
from net2vec.domain.corpus import CorpusIngestionRun, CorpusSourceOutcome
from net2vec.embeddings.factory import EmbeddingConfigurationError, create_embedding_service
from net2vec.ingestion.corpus import CorpusIngestionService
from net2vec.ingestion.fetcher import HttpFetcher
from net2vec.ingestion.manifest import DEFAULT_MANIFEST_PATH, ManifestValidationError, load_manifest
from net2vec.ingestion.pipeline import IngestionPipeline
from net2vec.persistence.database import (
    DatabaseConnectionError,
    create_session_factory,
    verify_database_connection,
)
from net2vec.persistence.repositories import SqlAlchemyDocumentRepository


def ingest_corpus(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    *,
    debug: bool = False,
    offline: bool = False,
    disable_safetensors_conversion: bool = False,
) -> int:
    _configure_logging(debug)
    _configure_model_loading(offline, disable_safetensors_conversion)
    try:
        manifest = load_manifest(manifest_path)
        run = _run_manifest(manifest, _print_outcome)
    except (ManifestValidationError, EmbeddingConfigurationError, DatabaseConnectionError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    _print_summary(run)
    return 1 if run.failed else 0


def _run_manifest(manifest, on_outcome=None) -> CorpusIngestionRun:  # noqa: ANN001
    settings = Settings.from_env()
    session = create_session_factory(settings.database_url)()
    try:
        verify_database_connection(session)
        pipeline = IngestionPipeline(
            fetcher=HttpFetcher(),
            embedding_service=create_embedding_service(settings),
            repository=SqlAlchemyDocumentRepository(session),
        )
        return CorpusIngestionService(pipeline).ingest(manifest, on_outcome=on_outcome)
    finally:
        session.close()


def _print_summary(run: CorpusIngestionRun) -> None:
    print(
        f"corpus {run.corpus_id}: {run.succeeded} succeeded, "
        f"{run.failed} failed, {run.skipped} skipped",
        flush=True,
    )


def _print_outcome(outcome: CorpusSourceOutcome) -> None:
    print(_outcome_line(outcome), flush=True)


def _configure_logging(debug: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)


def _configure_model_loading(offline: bool, disable_conversion: bool) -> None:
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if disable_conversion:
        os.environ["DISABLE_SAFETENSORS_CONVERSION"] = "1"


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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show detailed diagnostic logs and unexpected exception tracebacks",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="load Hugging Face model files from the local cache; source URLs are still fetched",
    )
    parser.add_argument(
        "--disable-safetensors-conversion",
        action="store_true",
        help="disable Transformers' automatic safetensors conversion and download",
    )
    args = parser.parse_args()
    raise SystemExit(
        ingest_corpus(
            args.manifest,
            debug=args.debug,
            offline=args.offline,
            disable_safetensors_conversion=args.disable_safetensors_conversion,
        )
    )


if __name__ == "__main__":
    main()
