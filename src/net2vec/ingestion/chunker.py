"""Heading-aware chunk construction."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChunkDraft:
    chunk_index: int
    heading_path: tuple[str, ...]
    heading_text: str | None
    excerpt: str
    full_chunk_text: str
    token_count: int
    content_hash: str


class BlockLike(Protocol):
    kind: str
    level: int
    text: str


def build_chunks(
    blocks: Iterable[BlockLike | tuple[str, int, str]],
    source_url: str,
    max_words: int = 450,
) -> list[ChunkDraft]:
    del source_url
    state = ChunkState(max_words=max_words)
    for block in blocks:
        state.accept(_coerce_block(block))
    return state.finish()


class ChunkState:
    def __init__(self, max_words: int) -> None:
        self.max_words = max_words
        self.heading_path: list[str] = []
        self.pending: list[str] = []
        self.chunks: list[ChunkDraft] = []

    def accept(self, block: BlockLike) -> None:
        if block.kind == "heading":
            self._set_heading(block.level, block.text)
            return
        self._add_text(block.text)

    def finish(self) -> list[ChunkDraft]:
        self._flush()
        return self.chunks

    def _set_heading(self, level: int, text: str) -> None:
        self._flush()
        self.heading_path = self.heading_path[: max(level - 1, 0)]
        self.heading_path.append(text)

    def _add_text(self, text: str) -> None:
        if _word_count(" ".join([*self.pending, text])) > self.max_words:
            self._flush()
        self.pending.append(text)

    def _flush(self) -> None:
        full_text = " ".join(self.pending).strip()
        if not full_text:
            return
        self.chunks.append(_chunk(len(self.chunks), tuple(self.heading_path), full_text))
        self.pending = []


def _coerce_block(block: BlockLike | tuple[str, int, str]) -> BlockLike:
    if isinstance(block, tuple):
        return TupleBlock(kind=block[0], level=block[1], text=block[2])
    return block


@dataclass(frozen=True)
class TupleBlock:
    kind: str
    level: int
    text: str


def _chunk(index: int, heading_path: tuple[str, ...], text: str) -> ChunkDraft:
    return ChunkDraft(
        chunk_index=index,
        heading_path=heading_path,
        heading_text=heading_path[-1] if heading_path else None,
        excerpt=_excerpt(text),
        full_chunk_text=text,
        token_count=_word_count(text),
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def _excerpt(text: str, max_chars: int = 280) -> str:
    return text if len(text) <= max_chars else f"{text[: max_chars - 1].rstrip()}..."


def _word_count(text: str) -> int:
    return len(text.split())
