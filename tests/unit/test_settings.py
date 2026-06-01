import pytest

from net2vec.config.settings import Settings


def test_settings_default_to_local_codebert(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NET2VEC_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("NET2VEC_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("NET2VEC_EMBEDDING_DIMENSIONS", raising=False)

    settings = Settings.from_env()

    assert settings.embedding_provider == "local"
    assert settings.embedding_model == "microsoft/codebert-base"
    assert settings.embedding_dimensions == 768


def test_settings_accept_openai_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NET2VEC_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("NET2VEC_EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("NET2VEC_EMBEDDING_DIMENSIONS", "1536")

    settings = Settings.from_env()

    assert settings.embedding_provider == "openai"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.embedding_dimensions == 1536


def test_settings_reject_unknown_embedding_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NET2VEC_EMBEDDING_PROVIDER", "banana")

    with pytest.raises(ValueError, match="unsupported embedding provider"):
        Settings.from_env()
