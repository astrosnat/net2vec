# Quickstart: Local Embedding Provider

## 1. Install Development Dependencies

```powershell
python -m pip install -e ".[dev]"
```

Expected result: package imports, test tools, and local embedding dependencies are available.

## 2. Configure Local Embeddings

```powershell
$env:DATABASE_URL = "postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec"
$env:NET2VEC_EMBEDDING_PROVIDER = "local"
$env:NET2VEC_EMBEDDING_MODEL = "microsoft/codebert-base"
$env:NET2VEC_EMBEDDING_DIMENSIONS = "768"
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

Expected result: net2vec uses local embeddings and does not require an external embedding API key.

## 3. Prepare the Database

```powershell
python -m net2vec.persistence.migrations upgrade
```

Expected result: database tables exist, pgvector is enabled, and the document-section embedding column accepts 768-dimensional vectors.

If the local database was previously created with 1536-dimensional vectors, recreate or migrate it before continuing.

## 4. Ingest One Exact Documentation URL

```powershell
python -m net2vec.cli.ingest "https://go.dev/doc/effective_go"
```

Expected result:

- The submitted page is fetched.
- Linked pages are not crawled.
- Heading-aware chunks are stored.
- Chunks are embedded locally.
- Stored vector metadata reports 768 dimensions.

## 5. Start the Search API

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

Expected result: ranked results include `excerpt`, `full_chunk_text`, `source_url`, `heading_path`, `rank`, and `score`.

## 6. Start the MCP Server

```powershell
python -m net2vec.mcp.server
```

Expected result: the local/internal MCP server exposes `search_docs`, and query embeddings are generated with the configured local provider.

## 7. Run Validation

```powershell
pytest
ruff check .
lizard -C 3 src tests
```

Expected result: tests pass, style checks pass, and all functions stay below the project complexity limit.
