import pytest

from net2vec.domain.documents import IngestionError
from net2vec.ingestion.fetcher import validate_exact_url


def test_accepts_exact_http_url_without_fragment() -> None:
    assert validate_exact_url("https://go.dev/doc/effective_go") == "https://go.dev/doc/effective_go"


def test_rejects_non_http_schemes() -> None:
    with pytest.raises(IngestionError):
        validate_exact_url("file:///tmp/doc.html")


def test_rejects_fragment_urls_to_keep_exact_page_scope() -> None:
    with pytest.raises(IngestionError):
        validate_exact_url("https://go.dev/doc/effective_go#names")
