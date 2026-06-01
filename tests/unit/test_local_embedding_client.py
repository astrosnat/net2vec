from types import SimpleNamespace

import pytest
import torch

from net2vec.embeddings.client import LocalEmbeddingClient


class FakeTokenizer:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str]] = []

    def __call__(self, texts, padding: bool, truncation: bool, return_tensors: str):
        self.calls.append((texts, return_tensors))
        return {
            "input_ids": torch.tensor([[101, 102, 0], [101, 200, 102]]),
            "attention_mask": torch.tensor([[1, 1, 0], [1, 1, 1]]),
        }


class FakeModel:
    def __init__(self) -> None:
        self.eval_called = False
        self.inference_modes: list[bool] = []

    def eval(self) -> None:
        self.eval_called = True

    def __call__(self, **encoded):
        self.inference_modes.append(torch.is_inference_mode_enabled())
        hidden = torch.tensor(
            [
                [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [9.0, 9.0, 9.0]],
                [[0.0, 0.0, 2.0], [0.0, 0.0, 2.0], [0.0, 0.0, 2.0]],
            ],
        )
        return SimpleNamespace(last_hidden_state=hidden)


def test_local_embedding_client_pools_masks_and_normalizes() -> None:
    model = FakeModel()
    client = LocalEmbeddingClient(tokenizer=FakeTokenizer(), model_runner=model)

    vectors = client.embed(["one", "two"], "microsoft/codebert-base")

    assert vectors[0] == pytest.approx([0.7071067, 0.7071067, 0.0])
    assert vectors[1] == pytest.approx([0.0, 0.0, 1.0])
    assert model.eval_called is True


def test_local_embedding_client_runs_in_inference_mode() -> None:
    model = FakeModel()
    client = LocalEmbeddingClient(tokenizer=FakeTokenizer(), model_runner=model)

    client.embed(["one"], "microsoft/codebert-base")

    assert model.inference_modes == [True]
