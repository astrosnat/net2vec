from net2vec.config.codex import codex_mcp_snippet


def test_codex_mcp_snippet_uses_default_net2vec_server() -> None:
    assert codex_mcp_snippet() == (
        '[mcp_servers.net2vec]\n'
        'url = "http://127.0.0.1:8001/mcp"\n'
    )


def test_codex_mcp_snippet_accepts_custom_server_details() -> None:
    assert codex_mcp_snippet("docs", "http://localhost:9000/mcp") == (
        '[mcp_servers.docs]\n'
        'url = "http://localhost:9000/mcp"\n'
    )
