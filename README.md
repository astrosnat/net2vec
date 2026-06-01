# net2vec

`net2vec` is a small tool developed to ingest texts from the web, vector embed them, and connect them to AI agents. `net2vec` is designed to make automated software development easier and more token-efficient.

## Local Development

Use Python 3.14.

```powershell
python -m pip install -e ".[dev]"
pytest
ruff check .
lizard -C 3 src tests
```

Copy `.env.example` to `.env` or export the variables in your shell before
running ingestion. The first feature quickstart is in
`specs/001-docs-vector-ingestion/quickstart.md`.

## Quickstart

## 1. Configure Environment

```powershell
$env:DATABASE_URL = "postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec"
$env:NET2VEC_EMBEDDING_PROVIDER = "local"
$env:NET2VEC_EMBEDDING_MODEL = "microsoft/codebert-base"
$env:NET2VEC_EMBEDDING_DIMENSIONS = "768"
```

Local embedding mode uses Hugging Face Transformers and PyTorch, and does not
require `OPENAI_API_KEY`. To use the external OpenAI embedding API instead, set
`NET2VEC_EMBEDDING_PROVIDER` to `openai`, configure an OpenAI embedding model
and matching dimensions, and provide `OPENAI_API_KEY`.

## 2. Prepare the Database

```powershell
python -m net2vec.persistence.migrations upgrade
```

Expected result: database tables exist, pgvector is enabled for embeddings, and
the document-section embedding column accepts 768-dimensional CodeBERT vectors.

Existing local databases created before the local embedding default may still
have a 1536-dimensional vector column. Recreate the local database or apply an
explicit migration before ingesting 768-dimensional local embeddings.

## 3. Ingest One Exact Documentation URL

```powershell
python -m net2vec.cli.ingest "https://go.dev/doc/effective_go"
```

Expected result:

- Exactly the submitted page is fetched.
- Linked pages are not crawled.
- Heading-aware chunks are stored.
- Chunks are embedded with CodeBERT.
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

Print the local Codex MCP configuration:

```powershell
python -m net2vec.cli.configure
```

Add the printed local MCP server block to `~/.codex/config.toml`:

```toml
[mcp_servers.net2vec]
url = "http://127.0.0.1:8001/mcp"
```

Official Codex documentation also supports adding MCP servers with the Codex
CLI and checking them with `codex mcp list`.
