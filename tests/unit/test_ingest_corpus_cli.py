import json
from datetime import UTC, datetime
from types import SimpleNamespace
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
        lambda manifest, on_outcome: _stream_run(
            on_outcome,
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
    monkeypatch.setattr(
        cli,
        "_run_manifest",
        lambda manifest, callback: _stream_run(callback, failed),
    )

    assert cli.ingest_corpus(path) == 1


def test_cli_returns_two_before_running_invalid_manifest(tmp_path, monkeypatch, capsys) -> None:  # noqa: ANN001
    path = tmp_path / "invalid.json"
    path.write_text("{}", encoding="utf-8")
    called = False

    def run_manifest(manifest, callback):  # noqa: ANN001
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "_run_manifest", run_manifest)

    assert cli.ingest_corpus(path) == 2
    assert called is False
    assert "configuration error" in capsys.readouterr().err


def test_cli_configures_offline_model_loading_before_run(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    path = _write_manifest(tmp_path)
    observed = {}

    def run_manifest(manifest, callback):  # noqa: ANN001
        observed["hf"] = cli.os.environ.get("HF_HUB_OFFLINE")
        observed["transformers"] = cli.os.environ.get("TRANSFORMERS_OFFLINE")
        observed["conversion"] = cli.os.environ.get("DISABLE_SAFETENSORS_CONVERSION")
        return _run()

    monkeypatch.setattr(cli, "_run_manifest", run_manifest)

    result = cli.ingest_corpus(path, offline=True, disable_safetensors_conversion=True)

    assert result == 0
    assert observed == {"hf": "1", "transformers": "1", "conversion": "1"}


def test_run_manifest_checks_database_before_creating_embedding_service(monkeypatch) -> None:  # noqa: ANN001
    session = SimpleNamespace(close=lambda: None)
    calls = []
    monkeypatch.setattr(cli, "create_session_factory", lambda url: lambda: session)
    monkeypatch.setattr(cli, "verify_database_connection", lambda value: calls.append("database"))
    monkeypatch.setattr(cli, "create_embedding_service", lambda settings: calls.append("embedding"))
    monkeypatch.setattr(cli, "IngestionPipeline", lambda **kwargs: SimpleNamespace())
    monkeypatch.setattr(
        cli.CorpusIngestionService,
        "ingest",
        lambda self, manifest, on_outcome: _run(),
    )

    cli._run_manifest(SimpleNamespace())

    assert calls == ["database", "embedding"]


def _stream_run(callback, *outcomes):  # noqa: ANN001, ANN202
    for outcome in outcomes:
        callback(outcome)
    return _run(*outcomes)
