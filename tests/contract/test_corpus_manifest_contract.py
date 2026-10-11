import json
from pathlib import Path

from net2vec.ingestion.manifest import DEFAULT_MANIFEST_PATH, load_manifest

SCHEMA_PATH = Path("specs/003-go-corpus-extraction/contracts/corpus-manifest.schema.json")


def test_default_manifest_matches_contract_shape() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert set(manifest) == set(schema["required"])
    source_fields = set(schema["$defs"]["source"]["required"])
    assert all(set(source) == source_fields for source in manifest["sources"])
    assert manifest["schema_version"] == schema["properties"]["schema_version"]["const"]


def test_default_manifest_contains_seven_approved_sources() -> None:
    manifest = load_manifest()

    assert len(manifest.sources) == 7
    assert all(source.enabled for source in manifest.sources)
    assert {source.id for source in manifest.sources} == {
        "google-go-overview",
        "google-go-guide",
        "google-go-decisions",
        "google-go-best-practices",
        "effective-go",
        "go-code-review-comments",
        "go-test-comments",
    }
