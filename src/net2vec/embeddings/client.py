"""Embedding client interfaces and adapters."""

from __future__ import annotations

from typing import Protocol


class EmbeddingClient(Protocol):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        """Return one embedding vector per input text."""


class OpenAIEmbeddingClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]
