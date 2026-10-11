import json
from pathlib import Path

import pytest

from net2vec.ingestion.extractor import extract_page

FIXTURE_DIR = Path("tests/fixtures/extraction")


def test_extracts_title_headings_and_content() -> None:
    html = """
    <html>
      <head><title>Effective Go</title></head>
      <body>
        <nav>Skip this</nav>
        <h1>Names</h1>
        <p>MixedCaps or mixedCaps rather than underscores.</p>
      </body>
    </html>
    """

    page = extract_page(html)

    assert page.title == "Effective Go"
    assert [block.text for block in page.blocks] == [
        "Names",
        "MixedCaps or mixedCaps rather than underscores.",
    ]


def test_ignores_script_style_and_boilerplate() -> None:
    html = "<main><script>x()</script><style>x</style><p>Keep me</p><footer>Drop</footer></main>"
    page = extract_page(html)

    assert page.text == "Keep me"


@pytest.mark.parametrize("fixture_name", ["google_style.html", "go_dev_guide.html"])
def test_extracts_source_family_fixture_as_ordered_semantic_blocks(fixture_name: str) -> None:
    expected = _expected()[fixture_name]

    page = extract_page((FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"))

    assert page.title == expected["title"]
    assert [
        {"kind": block.kind, "level": block.level, "text": block.text}
        for block in page.blocks
    ] == expected["blocks"]


def test_nested_inline_content_appears_once_in_reading_order() -> None:
    page = extract_page("<main><p>Use <code>MixedCaps</code>, not snake case.</p></main>")

    assert page.text == "Use MixedCaps, not snake case."
    assert page.text.count("MixedCaps") == 1


def test_empty_or_boilerplate_only_page_has_no_blocks() -> None:
    page = extract_page("<html><nav>Only navigation</nav><script>x()</script></html>")

    assert page.blocks == ()


def _expected() -> dict:
    return json.loads((FIXTURE_DIR / "expected_blocks.json").read_text(encoding="utf-8"))
