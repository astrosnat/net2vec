import json

import pytest

from net2vec.ingestion.manifest import ManifestValidationError, load_manifest


def _manifest() -> dict:
    return {
        "schema_version": 1,
        "corpus_id": "go-style",
        "title": "Go Style",
        "sources": [
            {
                "id": "guide",
                "url": "https://example.com/guide",
                "title": "Guide",
                "classification": "canonical",
                "enabled": True,
            },
        ],
    }


def _write(tmp_path, data) -> str:  # noqa: ANN001
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_rejects_malformed_json(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ManifestValidationError, match="cannot read"):
        load_manifest(path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.update(schema_version=2), "schema version"),
        (lambda data: data.pop("title"), "fields must be exactly"),
        (lambda data: data["sources"][0].update(classification="other"), "classification"),
        (lambda data: data["sources"][0].update(enabled="yes"), "enabled must be boolean"),
    ],
)
def test_rejects_invalid_manifest_values(tmp_path, mutation, message: str) -> None:  # noqa: ANN001
    data = _manifest()
    mutation(data)

    with pytest.raises(ManifestValidationError, match=message):
        load_manifest(_write(tmp_path, data))


def test_rejects_duplicate_ids_and_normalized_urls(tmp_path) -> None:
    data = _manifest()
    duplicate = dict(data["sources"][0], url="https://example.com/other")
    data["sources"].append(duplicate)
    with pytest.raises(ManifestValidationError, match="duplicate source id"):
        load_manifest(_write(tmp_path, data))

    data = _manifest()
    duplicate = dict(data["sources"][0], id="other", url="https://example.com/guide/")
    data["sources"].append(duplicate)
    with pytest.raises(ManifestValidationError, match="duplicate source URL"):
        load_manifest(_write(tmp_path, data))


def test_rejects_manifest_without_enabled_sources(tmp_path) -> None:
    data = _manifest()
    data["sources"][0]["enabled"] = False

    with pytest.raises(ManifestValidationError, match="enabled source"):
        load_manifest(_write(tmp_path, data))
