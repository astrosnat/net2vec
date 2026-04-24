"""HTML extraction with lightweight boilerplate removal."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser

IGNORED_TAGS = {"script", "style", "nav", "header", "footer", "aside", "noscript"}
BLOCK_TAGS = {"p", "li", "pre", "code", "blockquote"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


@dataclass(frozen=True)
class ExtractedBlock:
    kind: str
    level: int
    text: str


@dataclass(frozen=True)
class ExtractedPage:
    title: str | None
    blocks: tuple[ExtractedBlock, ...]

    @property
    def text(self) -> str:
        return "\n".join(block.text for block in self.blocks if block.kind == "text")


def extract_page(html: str) -> ExtractedPage:
    parser = DocumentationHTMLParser()
    parser.feed(html)
    parser.close()
    return ExtractedPage(title=parser.title_text, blocks=tuple(parser.blocks))


class DocumentationHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[ExtractedBlock] = []
        self.title_text: str | None = None
        self._ignored_depth = 0
        self._current_tag: str | None = None
        self._current_level = 0
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in IGNORED_TAGS:
            self._ignored_depth += 1
        self._start_capture(tag)

    def handle_endtag(self, tag: str) -> None:
        self._finish_capture(tag)
        if tag in IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth or self._current_tag is None:
            return
        self._buffer.append(data)

    def _start_capture(self, tag: str) -> None:
        if self._ignored_depth or tag not in BLOCK_TAGS | HEADING_TAGS | {"title"}:
            return
        self._current_tag = tag
        self._current_level = _heading_level(tag)
        self._buffer = []

    def _finish_capture(self, tag: str) -> None:
        if tag != self._current_tag:
            return
        self._commit_buffer(tag)
        self._current_tag = None

    def _commit_buffer(self, tag: str) -> None:
        text = _clean_text(" ".join(self._buffer))
        if not text:
            return
        self._store_text(tag, text)

    def _store_text(self, tag: str, text: str) -> None:
        if tag == "title":
            self.title_text = text
            return
        self.blocks.append(_block(tag, self._current_level, text))


def _block(tag: str, level: int, text: str) -> ExtractedBlock:
    kind = "heading" if tag in HEADING_TAGS else "text"
    return ExtractedBlock(kind=kind, level=level, text=text)


def _heading_level(tag: str) -> int:
    return int(tag[1]) if tag in HEADING_TAGS else 0


def _clean_text(text: str) -> str:
    return " ".join(text.split())
