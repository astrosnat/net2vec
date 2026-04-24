"""Runtime settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    openai_api_key: str | None
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
            embedding_model=_env("NET2VEC_EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dimensions=_int_env("NET2VEC_EMBEDDING_DIMENSIONS", 1536),
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
