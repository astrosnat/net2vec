"""Semantic documentation extraction with nested-markup preservation."""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

IGNORED_TAGS = ("script", "style", "nav", "header", "footer", "aside", "noscript")
HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
CONTENT_TAGS = HEADING_TAGS | {"p", "pre", "code", "li", "tr", "blockquote"}
STRUCTURED_KINDS = {"pre": "code", "code": "code", "li": "list-item", "tr": "table-row"}


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
    soup = BeautifulSoup(html, "lxml")
    title = _page_title(soup)
    _remove_ignored_content(soup)
    root = _content_root(soup)
    blocks = tuple(_blocks(root))
    return ExtractedPage(title=title, blocks=blocks)


def _page_title(soup: BeautifulSoup) -> str | None:
    title = soup.title
    return _normalized_text(title) if title else None


def _remove_ignored_content(soup: BeautifulSoup) -> None:
    for element in soup.find_all(IGNORED_TAGS):
        element.decompose()


def _content_root(soup: BeautifulSoup) -> Tag | BeautifulSoup:
    root = soup.select_one("main, article, body")
    return root if root else soup


def _blocks(root: Tag | BeautifulSoup):  # noqa: ANN202
    for element in _outer_elements(root):
        block = _block(element)
        if block.text:
            yield block


def _outer_elements(root: Tag | BeautifulSoup):  # noqa: ANN202
    for element in root.find_all(CONTENT_TAGS):
        if not _has_semantic_ancestor(element, root):
            yield element


def _has_semantic_ancestor(element: Tag, root: Tag | BeautifulSoup) -> bool:
    ancestor = element.find_parent(CONTENT_TAGS)
    return ancestor is not None and ancestor is not root


def _block(element: Tag) -> ExtractedBlock:
    return ExtractedBlock(
        kind=_block_kind(element.name),
        level=_heading_level(element.name),
        text=_block_text(element),
    )


def _block_kind(tag: str) -> str:
    if tag in HEADING_TAGS:
        return "heading"
    return STRUCTURED_KINDS.get(tag, "text")


def _heading_level(tag: str) -> int:
    return int(tag[1]) if tag in HEADING_TAGS else 0


def _block_text(element: Tag) -> str:
    if element.name in {"pre", "code"}:
        return _code_text(element)
    if element.name == "tr":
        return _table_row_text(element)
    return _normalized_text(element)


def _code_text(element: Tag) -> str:
    return element.get_text().strip("\n")


def _table_row_text(element: Tag) -> str:
    cells = element.find_all(("th", "td"), recursive=False)
    return " | ".join(filter(None, (_normalized_text(cell) for cell in cells)))


def _normalized_text(element: Tag) -> str:
    return " ".join(element.get_text().split())
