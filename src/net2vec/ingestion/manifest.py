"""Loading and validation for checked-in corpus manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from net2vec.domain.corpus import CorpusManifest, CorpusSource, SourceClassification
from net2vec.domain.documents import IngestionError

DEFAULT_MANIFEST_PATH = Path(__file__).parents[1] / "config" / "corpora" / "go-style.json"
MANIFEST_FIELDS = frozenset({"schema_version", "corpus_id", "title", "sources"})
SOURCE_FIELDS = frozenset({"id", "url", "title", "classification", "enabled"})


class ManifestValidationError(IngestionError):
    """Raised when a corpus manifest is malformed or invalid."""


def load_manifest(path: str | Path = DEFAULT_MANIFEST_PATH) -> CorpusManifest:
    data = _read_json(Path(path))
    root = _object(data, "manifest")
    _require_fields(root, MANIFEST_FIELDS, "manifest")
    sources = tuple(_source(item, index) for index, item in enumerate(_source_items(root)))
    return _manifest(root, sources)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestValidationError(f"cannot read corpus manifest: {exc}") from exc


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestValidationError(f"{label} must be an object")
    return value


def _require_fields(value: dict[str, Any], expected: frozenset[str], label: str) -> None:
    actual = frozenset(value)
    if actual != expected:
        fields = ", ".join(sorted(expected))
        raise ManifestValidationError(f"{label} fields must be exactly: {fields}")


def _source_items(root: dict[str, Any]) -> list[Any]:
    sources = root["sources"]
    if not isinstance(sources, list):
        raise ManifestValidationError("manifest sources must be an array")
    return sources


def _source(value: Any, index: int) -> CorpusSource:
    data = _object(value, f"source {index}")
    _require_fields(data, SOURCE_FIELDS, f"source {index}")
    try:
        return CorpusSource(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            classification=_classification(data["classification"], index),
            enabled=_boolean(data["enabled"], index),
        )
    except (TypeError, ValueError) as exc:
        raise ManifestValidationError(f"invalid source {index}: {exc}") from exc


def _boolean(value: Any, index: int) -> bool:
    if not isinstance(value, bool):
        raise ManifestValidationError(f"source {index} enabled must be boolean")
    return value


def _classification(value: Any, index: int) -> SourceClassification:
    try:
        return SourceClassification(value)
    except (TypeError, ValueError) as exc:
        raise ManifestValidationError(f"source {index} has unsupported classification") from exc


def _manifest(root: dict[str, Any], sources: tuple[CorpusSource, ...]) -> CorpusManifest:
    try:
        return CorpusManifest(
            schema_version=root["schema_version"],
            corpus_id=root["corpus_id"],
            title=root["title"],
            sources=sources,
        )
    except (TypeError, ValueError) as exc:
        raise ManifestValidationError(f"invalid corpus manifest: {exc}") from exc
