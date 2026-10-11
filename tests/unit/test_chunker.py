from net2vec.ingestion.chunker import build_chunks


def test_builds_heading_aware_chunks() -> None:
    chunks = build_chunks(
        [
            ("heading", 1, "Names"),
            ("text", 0, "MixedCaps are preferred."),
            ("heading", 2, "Package names"),
            ("text", 0, "Use short package names."),
        ],
        source_url="https://go.dev/doc/effective_go",
        max_words=10,
    )

    assert [chunk.heading_path for chunk in chunks] == [("Names",), ("Names", "Package names")]
    assert chunks[0].full_chunk_text == "MixedCaps are preferred."


def test_uses_empty_heading_path_when_page_has_no_heading() -> None:
    chunks = build_chunks([("text", 0, "Plain documentation text.")], source_url="https://example.com")

    assert chunks[0].heading_path == ()
    assert chunks[0].excerpt == "Plain documentation text."


def test_preserves_structured_block_boundaries() -> None:
    chunks = build_chunks(
        [
            ("text", 0, "Good:"),
            ("code", 0, "func good() {\n\treturn\n}"),
            ("text", 0, "Use this form."),
            ("list-item", 0, "First rule"),
            ("list-item", 0, "Second rule"),
        ],
        source_url="https://example.com/guide",
    )

    assert chunks[0].full_chunk_text == (
        "Good:\n\nfunc good() {\n\treturn\n}\n\nUse this form.\n\nFirst rule\n\nSecond rule"
    )
