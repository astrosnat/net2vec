# Implementation Plan: Local Embedding Provider

**Branch**: `002-local-hf-embeddings` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-local-hf-embeddings/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a local embedding provider so developers can ingest and search documentation without an external embedding API key. The implementation will keep the existing embedding service contract, add a shared provider-selection boundary used by CLI, HTTP, and MCP entry points, use CodeBERT-sized local vectors by default, and align pgvector storage with the 768-dimensional local model.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.x, Alembic, psycopg 3, pgvector-python, OpenAI SDK, Hugging Face Transformers, PyTorch, BeautifulSoup4, lxml, httpx, MCP Python SDK, pytest, ruff, lizard  
**Storage**: PostgreSQL 16+ with pgvector, document-section embeddings stored as fixed-dimension vectors  
**Testing**: pytest, ruff, lizard complexity gate  
**Target Platform**: Local developer workstation and trusted local/internal service runtime  
**Project Type**: Python package with CLI, HTTP API, MCP server, ingestion services, and persistence adapters  
**Performance Goals**: One-page documentation ingestion and one search query complete reliably on local CPU for developer workflows; local model loads once per provider instance rather than once per text  
**Constraints**: Functions and methods must keep cyclomatic complexity at 3 or below; model-specific behavior must remain behind embedding adapters; external API credentials must not be required for local mode; stored vector dimension must match active embedding configuration  
**Scale/Scope**: Single-node local/internal documentation retrieval for exact submitted URLs; mixed historical vector dimensions are out of scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Complexity Under Four**: PASS. Planned branching is limited to small settings/provider factory helpers. Adapter methods will be decomposed into model loading, tokenization, pooling, and conversion helpers if needed.
- **SOLID Design**: PASS. The existing `EmbeddingClient` protocol remains the stable dependency. OpenAI and local clients are interchangeable adapters, while entry points depend on a shared factory rather than concrete clients.
- **Separation of Concerns**: PASS. Ingestion, parsing, storage, retrieval, API routing, and MCP handling keep delegating to `EmbeddingService`; only embedding adapter/factory/settings modules know provider details.
- **Testable Agent-Facing Behavior**: PASS. MCP `search_docs` behavior remains contract-compatible while using the configured embedding provider. Tests will cover factory selection, local embedding dimensions, query embedding reuse, and MCP search with injected/fake services.
- **Explicit Boundaries**: PASS. A new provider setting, default model/dimension values, embedding metadata semantics, and pgvector dimension migration/model changes are explicit data and integration boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/002-local-hf-embeddings/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- embedding-configuration.md
|   |-- vector-storage.md
|-- checklists/
|   |-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/
|-- net2vec/
|   |-- api/
|   |   `-- routes.py
|   |-- cli/
|   |   `-- ingest.py
|   |-- config/
|   |   `-- settings.py
|   |-- embeddings/
|   |   |-- client.py
|   |   |-- factory.py
|   |   `-- service.py
|   |-- mcp/
|   |   `-- server.py
|   `-- persistence/
|       |-- migrations/
|       |   `-- versions/
|       |       `-- 0001_enable_pgvector.py
|       `-- models.py
tests/
|-- contract/
|   |-- test_http_search_contract.py
|   `-- test_mcp_search_docs_contract.py
|-- integration/
|   |-- test_ingest_refresh_flow.py
|   `-- test_search_flow.py
`-- unit/
    |-- test_embedding_factory.py
    |-- test_embedding_service.py
    `-- test_repositories.py
```

**Structure Decision**: Use the existing single Python package layout. Add only an embedding factory module and local adapter inside `net2vec.embeddings`; update current entry points to call the factory so provider selection stays centralized.

## Complexity Tracking

No constitution violations identified.

## Phase 0: Research Summary

Research output is captured in [research.md](./research.md). Key decisions:

- Use `NET2VEC_EMBEDDING_PROVIDER` with values `local` and `openai`; default to `local`.
- Use `microsoft/codebert-base` and `768` dimensions for local mode.
- Load local models through Hugging Face Transformers and run PyTorch inference in eval/inference mode.
- Use deterministic last-hidden-state masked mean pooling and optional L2 normalization for local document/query vectors.
- Align SQLAlchemy and Alembic vector definitions to `Vector(768)` for the default local storage contract.

## Phase 1: Design Summary

Design output is captured in [data-model.md](./data-model.md), [quickstart.md](./quickstart.md), and [contracts/](./contracts/).

### Post-Design Constitution Check

- **Complexity Under Four**: PASS. Provider validation, client creation, local pooling, and metadata helpers are planned as separate small functions.
- **SOLID Design**: PASS. Stable callers keep depending on `EmbeddingService` and `EmbeddingClient`; new provider support extends adapters/factory without embedding provider checks in API, CLI, MCP, ingestion, or search code.
- **Separation of Concerns**: PASS. Storage dimension updates remain in persistence model/migration; local model execution remains in embedding adapter; documentation/quickstart carries developer setup guidance.
- **Testable Agent-Facing Behavior**: PASS. Existing HTTP/MCP contract tests remain, while new unit/integration tests validate configured provider behavior and vector compatibility.
- **Explicit Boundaries**: PASS. Environment contract, vector storage contract, migration expectation, and embedding metadata expectations are documented.
