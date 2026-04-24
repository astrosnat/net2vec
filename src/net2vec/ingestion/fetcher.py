"""Exact-URL fetching for documentation pages."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse

import httpx

from net2vec.domain.documents import IngestionError


@dataclass(frozen=True)
class FetchResult:
    url: str
    html: str
    status_code: int | None = None


def validate_exact_url(url: str) -> str:
    parsed = urlparse(url.strip())
    _require_http_url(parsed.scheme, parsed.netloc)
    _reject_fragment(parsed.fragment)
    return urlunparse(parsed._replace(fragment=""))


def _require_http_url(scheme: str, netloc: str) -> None:
    if scheme not in {"http", "https"} or not netloc:
        raise IngestionError("URL must be an absolute HTTP or HTTPS URL")


def _reject_fragment(fragment: str) -> None:
    if fragment:
        raise IngestionError("URL fragments are not accepted for exact-page ingestion")


class HttpFetcher:
    def __init__(self, timeout_seconds: float = 20.0, max_redirects: int = 5) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_redirects = max_redirects

    def fetch(self, url: str) -> FetchResult:
        exact_url = validate_exact_url(url)
        with httpx.Client(follow_redirects=True, max_redirects=self.max_redirects) as client:
            response = client.get(exact_url, timeout=self.timeout_seconds)
        _raise_for_fetch_error(response)
        return FetchResult(
            url=str(response.url),
            html=response.text,
            status_code=response.status_code,
        )


def _raise_for_fetch_error(response: httpx.Response) -> None:
    content_type = response.headers.get("content-type", "")
    if response.status_code >= 400:
        raise IngestionError(f"URL fetch failed with status {response.status_code}")
    if "html" not in content_type.lower():
        raise IngestionError(f"URL returned unsupported content type: {content_type}")
