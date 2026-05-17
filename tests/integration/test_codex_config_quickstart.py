from pathlib import Path

from net2vec.config.codex import codex_mcp_snippet


def test_quickstart_documents_codex_mcp_configuration() -> None:
    quickstart = _quickstart()

    assert codex_mcp_snippet().strip() in quickstart
    assert "python -m net2vec.mcp.server" in quickstart
    assert "codex mcp list" in quickstart
    assert "search_docs" in quickstart


def test_quickstart_documents_local_internal_mcp_endpoint() -> None:
    quickstart = _quickstart()

    assert "http://127.0.0.1:8001/mcp" in quickstart
    assert "local/internal MCP server exposes the `search_docs` tool" in quickstart


def _quickstart() -> str:
    path = Path("specs/001-docs-vector-ingestion/quickstart.md")
    return path.read_text(encoding="utf-8")
