from net2vec.ingestion.extractor import extract_page


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
