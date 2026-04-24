# Quickstart: Documentation Vector Ingestion

This quickstart validates the planned end-to-end flow for one exact
documentation URL, local/internal search, and Codex access through `search_docs`.

## Prerequisites

- Python 3.12
- PostgreSQL 16+ with the pgvector extension available
- OpenAI API credentials for embedding generation
- Codex CLI or IDE extension using the shared Codex MCP configuration

## 1. Configure Environment

```powershell
$env:DATABASE_URL = "postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:NET2VEC_EMBEDDING_MODEL = "text-embedding-3-small"
```

## 2. Prepare the Database

```powershell
python -m net2vec.persistence.migrations upgrade
```

Expected result: database tables exist and pgvector is enabled for embeddings.

## 3. Ingest One Exact Documentation URL

```powershell
python -m net2vec.cli.ingest "https://go.dev/doc/effective_go"
```

Expected result:

- Exactly the submitted page is fetched.
- Linked pages are not crawled.
- Heading-aware chunks are stored.
- Re-running the command replaces the previous active content for that URL.

## 4. Start the Search API

```powershell
uvicorn net2vec.api.app:app --host 127.0.0.1 --port 8000
```

Validate search:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/search" `
  -ContentType "application/json" `
  -Body '{"query":"When should Go code use mixed caps?","limit":3}'
```

Expected result: ranked results include `excerpt`, `full_chunk_text`,
`source_url`, `heading_path`, `rank`, and `score`.

## 5. Start the MCP Server

```powershell
python -m net2vec.mcp.server
```

Expected result: local/internal MCP server exposes the `search_docs` tool.

## 6. Configure Codex

Add the local MCP server to `~/.codex/config.toml`:

```toml
[mcp_servers.net2vec]
url = "http://127.0.0.1:8001/mcp"
```

Official Codex documentation also supports adding MCP servers with the Codex
CLI and checking them with `codex mcp list`.

## 7. End-to-End Validation

Ask Codex a question whose answer appears in the ingested documentation, such as:

```text
Use search_docs to find the Effective Go guidance on mixed caps.
```

Expected result: Codex calls `search_docs`, receives relevant chunks, and can
cite or reference the returned source URL and heading path.

## Quality Gates

```powershell
pytest
ruff check .
lizard -C 3 src tests
```

Expected result: tests pass, lint passes, and no function or method has
cyclomatic complexity 4 or higher.
