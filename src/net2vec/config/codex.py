"""Codex configuration helpers."""


def codex_mcp_snippet(server_name: str = "net2vec", url: str = "http://127.0.0.1:8001/mcp") -> str:
    return f'[mcp_servers.{server_name}]\nurl = "{url}"\n'
