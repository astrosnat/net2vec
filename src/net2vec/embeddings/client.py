"""Embedding client interfaces and adapters."""

from __future__ import annotations

from typing import Any, Protocol


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


class LocalEmbeddingClient:
    def __init__(self, tokenizer: Any = None, model_runner: Any = None) -> None:
        self._tokenizer = tokenizer
        self._model_runner = model_runner

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        tokenizer, model_runner = self._components(model)
        encoded = _encoded_texts(tokenizer, texts)
        output = _run_model(model_runner, encoded)
        return _pooled_vectors(output.last_hidden_state, encoded["attention_mask"])

    def _components(self, model: str) -> tuple[Any, Any]:
        if self._has_components():
            return self._tokenizer, _prepared_model(self._model_runner)
        return self._load_components(model)

    def _has_components(self) -> bool:
        return self._tokenizer is not None and self._model_runner is not None

    def _load_components(self, model: str) -> tuple[Any, Any]:
        self._tokenizer, self._model_runner = _load_transformers_model(model)
        return self._tokenizer, _prepared_model(self._model_runner)


def _load_transformers_model(model: str) -> tuple[Any, Any]:
    from transformers import AutoModel, AutoTokenizer

    return AutoTokenizer.from_pretrained(model), AutoModel.from_pretrained(model)


def _prepared_model(model_runner: Any) -> Any:
    model_runner.eval()
    return model_runner


def _encoded_texts(tokenizer: Any, texts: list[str]) -> dict[str, Any]:
    return tokenizer(texts, padding=True, truncation=True, return_tensors="pt")


def _run_model(model_runner: Any, encoded: dict[str, Any]) -> Any:
    import torch

    with torch.inference_mode():
        return model_runner(**encoded)


def _pooled_vectors(last_hidden_state: Any, attention_mask: Any) -> list[list[float]]:
    mask = attention_mask.unsqueeze(-1).to(last_hidden_state.dtype)
    summed = (last_hidden_state * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1)
    return _normalized_rows(summed / counts).detach().cpu().tolist()


def _normalized_rows(vectors: Any) -> Any:
    denominator = vectors.norm(p=2, dim=1, keepdim=True).clamp(min=1e-12)
    return vectors / denominator
