import json
from datetime import UTC, datetime
from uuid import uuid4

from net2vec.cli import ingest_corpus as cli
from net2vec.domain.corpus import CorpusIngestionRun, CorpusSourceOutcome, CorpusSourceStatus


def _run(*outcomes: CorpusSourceOutcome) -> CorpusIngestionRun:
    now = datetime.now(UTC)
    return CorpusIngestionRun("go-style", now, now, outcomes)


def _outcome(status: CorpusSourceStatus, source_id: str = "guide") -> CorpusSourceOutcome:
    sections = {
        CorpusSourceStatus.SUCCEEDED: 2,
        CorpusSourceStatus.FAILED: 0,
        CorpusSourceStatus.SKIPPED: 0,
    }
    document_ids = {CorpusSourceStatus.SUCCEEDED: uuid4()}
    hashes = {CorpusSourceStatus.SUCCEEDED: "hash"}
    messages = {CorpusSourceStatus.SKIPPED: "disabled in manifest"}
    return CorpusSourceOutcome(
        source_id,
        f"https://example.com/{source_id}",
        status,
        sections[status],
        document_id=document_ids.get(status),
        content_hash=hashes.get(status),
        message=messages.get(status),
    )


def _write_manifest(tmp_path) -> str:  # noqa: ANN001
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "corpus_id": "go-style",
                "title": "Go",
                "sources": [
                    {
                        "id": "guide",
                        "url": "https://example.com/guide",
                        "title": "Guide",
                        "classification": "canonical",
                        "enabled": True,
                    },
                ],
            },
        ),
        encoding="utf-8",
    )
    return str(path)


def test_cli_reports_ordered_outcomes_and_success(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    path = _write_manifest(tmp_path)
    monkeypatch.setattr(
        cli,
        "_run_manifest",
        lambda manifest: _run(
            _outcome(CorpusSourceStatus.SUCCEEDED),
            _outcome(CorpusSourceStatus.SKIPPED, "disabled"),
        ),
    )

    exit_code = cli.ingest_corpus(path)

    lines = capsys.readouterr().out.splitlines()
    assert exit_code == 0
    assert lines == [
        "[succeeded] guide: 2 sections",
        "[skipped] disabled: disabled in manifest",
        "corpus go-style: 1 succeeded, 0 failed, 1 skipped",
    ]


def test_cli_returns_one_for_partial_failure(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    path = _write_manifest(tmp_path)
    failed = CorpusSourceOutcome(
        "guide",
        "https://example.com/guide",
        CorpusSourceStatus.FAILED,
        0,
        message="URL fetch failed with status 503",
    )
    monkeypatch.setattr(cli, "_run_manifest", lambda manifest: _run(failed))

    assert cli.ingest_corpus(path) == 1


def test_cli_returns_two_before_running_invalid_manifest(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    path = tmp_path / "invalid.json"
    path.write_text("{}", encoding="utf-8")
    called = False

    def run_manifest(manifest):  # noqa: ANN001
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "_run_manifest", run_manifest)

    assert cli.ingest_corpus(path) == 2
    assert called is False
    assert "manifest validation error" in capsys.readouterr().err
