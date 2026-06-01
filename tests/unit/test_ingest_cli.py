import pytest

from net2vec.cli import ingest
from net2vec.embeddings.factory import EmbeddingConfigurationError


def test_ingest_cli_exits_nonzero_for_embedding_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.argv", ["net2vec-ingest", "https://go.dev/doc/effective_go"])

    def fail_ingest(url: str) -> int:
        raise EmbeddingConfigurationError("OPENAI_API_KEY is required")

    monkeypatch.setattr(ingest, "ingest_url", fail_ingest)

    with pytest.raises(SystemExit) as exc:
        ingest.main()

    assert exc.value.code == 2
    assert "OPENAI_API_KEY is required" in capsys.readouterr().err
