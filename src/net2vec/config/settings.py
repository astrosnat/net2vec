"""Runtime settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

LOCAL_EMBEDDING_PROVIDER = "local"
OPENAI_EMBEDDING_PROVIDER = "openai"
SUPPORTED_EMBEDDING_PROVIDERS = frozenset(
    {LOCAL_EMBEDDING_PROVIDER, OPENAI_EMBEDDING_PROVIDER},
)
DEFAULT_EMBEDDING_PROVIDER = LOCAL_EMBEDDING_PROVIDER
DEFAULT_EMBEDDING_MODEL = "microsoft/codebert-base"
DEFAULT_EMBEDDING_DIMENSIONS = 768


@dataclass(frozen=True)
class Settings:
    database_url: str
    openai_api_key: str | None
    embedding_provider: str
    embedding_model: str
    embedding_dimensions: int
    api_host: str
    api_port: int
    mcp_url: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=_env(
                "DATABASE_URL",
                "postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec",
            ),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            embedding_provider=_embedding_provider(),
            embedding_model=_env("NET2VEC_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            embedding_dimensions=_int_env(
                "NET2VEC_EMBEDDING_DIMENSIONS",
                DEFAULT_EMBEDDING_DIMENSIONS,
            ),
            api_host=_env("NET2VEC_API_HOST", "127.0.0.1"),
            api_port=_int_env("NET2VEC_API_PORT", 8000),
            mcp_url=_env("NET2VEC_MCP_URL", "http://127.0.0.1:8001/mcp"),
        )


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _embedding_provider() -> str:
    provider = _env("NET2VEC_EMBEDDING_PROVIDER", DEFAULT_EMBEDDING_PROVIDER).lower()
    _validate_embedding_provider(provider)
    return provider


def _validate_embedding_provider(provider: str) -> None:
    if provider not in SUPPORTED_EMBEDDING_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_EMBEDDING_PROVIDERS))
        raise ValueError(f"unsupported embedding provider {provider!r}; use one of: {supported}")
