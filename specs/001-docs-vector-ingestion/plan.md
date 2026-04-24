# Implementation Plan: Documentation Vector Ingestion

**Branch**: `001-docs-vector-ingestion` | **Date**: 2026-04-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-docs-vector-ingestion/spec.md`

## Summary

Build a local/internal documentation retrieval system that ingests one exact
documentation URL at a time, extracts heading-aware chunks, embeds them, stores
one active version per URL in PostgreSQL with pgvector, exposes semantic search
through an HTTP API, and exposes the same search contract to Codex through an
MCP tool named `search_docs`.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Uvicorn, Typer, Pydantic, SQLAlchemy 2.x, Alembic, psycopg 3, pgvector-python, OpenAI Python SDK, BeautifulSoup4, lxml, httpx, MCP Python SDK, pytest, ruff, lizard  
**Storage**: PostgreSQL 16+ with pgvector 0.8.x extension  
**Testing**: pytest with unit, contract, and integration tests;
`lizard -C 3` for cyclomatic complexity; ruff for linting  
**Target Platform**: Local developer workstation and trusted internal network  
**Project Type**: Single Python project exposing CLI, HTTP API, and MCP server  
**Performance Goals**: Ingest one public documentation page and make it
searchable in under 2 minutes; return 95% of searches over a small local corpus
within 2 seconds; place expected answer chunks in top 3 for at least 90% of the
representative test queries  
**Constraints**: Exact-URL ingestion only; one active version per URL;
heading-aware chunks; trusted local/internal access only; Codex configuration
only; search results include excerpt and full stored chunk; every function or
method keeps cyclomatic complexity below 4  
**Scale/Scope**: Small to moderate documentation collections, not a web-scale
crawler; initial corpus target up to 1,000 source documents and 50,000 chunks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Complexity Under Four**: PASS. Branching-heavy behavior is decomposed into
  focused units: URL fetch policy, content extraction, heading tree traversal,
  chunk building, embedding orchestration, repository writes, search ranking,
  HTTP handlers, and MCP adapter functions. `lizard -C 3` is required to fail
  functions or methods with complexity 4 or higher.
- **SOLID Design**: PASS. Domain services depend on protocol-like ports for
  fetching, embedding, persistence, and search. FastAPI routes, Typer commands,
  and MCP tools are adapters that delegate to services rather than embedding
  business rules.
- **Separation of Concerns**: PASS. Ingestion, parsing, chunking, embedding,
  vector persistence, search, HTTP API, MCP tool exposure, and Codex config
  generation have separate modules and tests.
- **Testable Agent-Facing Behavior**: PASS. The `search_docs` contract has MCP
  contract tests, an end-to-end Codex configuration quickstart, and shared
  search service tests verifying excerpt, full chunk, URL, heading context, and
  relevance ordering.
- **Explicit Boundaries**: PASS. Data schemas are documented in
  `data-model.md`; HTTP and MCP contracts are documented in `contracts/`;
  refresh semantics replace active content by URL; no public authentication is
  claimed for the initial release.

## Project Structure

### Documentation (this feature)

```text
specs/001-docs-vector-ingestion/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- openapi.yaml
|   `-- mcp-search-docs.json
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/net2vec/
|-- __init__.py
|-- api/
|   |-- __init__.py
|   |-- app.py
|   `-- routes.py
|-- cli/
|   |-- __init__.py
|   `-- ingest.py
|-- config/
|   |-- __init__.py
|   |-- settings.py
|   `-- codex.py
|-- domain/
|   |-- __init__.py
|   |-- documents.py
|   |-- chunks.py
|   `-- search.py
|-- ingestion/
|   |-- __init__.py
|   |-- fetcher.py
|   |-- extractor.py
|   |-- chunker.py
|   `-- pipeline.py
|-- embeddings/
|   |-- __init__.py
|   |-- client.py
|   `-- service.py
|-- persistence/
|   |-- __init__.py
|   |-- database.py
|   |-- models.py
|   |-- repositories.py
|   `-- migrations/
|-- search/
|   |-- __init__.py
|   |-- service.py
|   `-- ranking.py
`-- mcp/
    |-- __init__.py
    `-- server.py

tests/
|-- contract/
|   |-- test_http_search_contract.py
|   `-- test_mcp_search_docs_contract.py
|-- integration/
|   |-- test_ingest_refresh_flow.py
|   |-- test_search_flow.py
|   `-- test_codex_config_quickstart.py
`-- unit/
    |-- test_chunker.py
    |-- test_extractor.py
    |-- test_search_service.py
    `-- test_repositories.py
```

**Structure Decision**: Use a single Python package because the feature is one
cohesive local/internal service with three adapters over the same domain
services: CLI ingestion, HTTP search, and MCP search. The split above keeps
concerns isolated without creating separate deployable projects.

## Complexity Tracking

No constitution violations are planned. If implementation discovers a function
that cannot stay below cyclomatic complexity 4, the task must either split the
function before merge or add a dated follow-up with a rejected simpler
alternative.
