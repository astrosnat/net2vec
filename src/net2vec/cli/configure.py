"""Print Codex MCP configuration."""

from __future__ import annotations

from net2vec.config.codex import codex_mcp_snippet
from net2vec.config.settings import Settings


def print_codex_config(server_name: str = "net2vec", url: str | None = None) -> int:
    print(codex_mcp_snippet(server_name, _url(url)), end="")
    return 0


def _url(url: str | None) -> str:
    return url or Settings.from_env().mcp_url


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Print Codex MCP configuration")
    parser.add_argument("--server-name", default="net2vec")
    parser.add_argument("--url")
    args = parser.parse_args()
    raise SystemExit(print_codex_config(args.server_name, args.url))


if __name__ == "__main__":
    main()
