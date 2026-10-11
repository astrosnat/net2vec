# Implementation Plan: Go Corpus Extraction

**Branch**: `003-go-corpus-extraction` | **Date**: 2026-10-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-go-corpus-extraction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the extractor's single active-buffer parser with semantic DOM traversal that preserves nested inline text, code layout, lists, tables, links, and example labels without duplicate capture. Add a checked-in, validated JSON manifest for seven approved Google and Go project guidance pages, plus a corpus ingestion service and CLI that reuse the existing per-URL pipeline, isolate failures per source, and report complete provenance and outcomes. Extend document/search metadata additively so retrieved sections can be traced to stable corpus and source identifiers while existing single-URL callers remain compatible.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: BeautifulSoup4 with lxml, Pydantic, SQLAlchemy 2.x, Alembic, httpx, existing embedding adapters, FastAPI, MCP Python SDK  
**Storage**: Checked-in JSON corpus manifest; PostgreSQL 16+ with pgvector for source documents, provenance, sections, and embeddings  
**Testing**: pytest with source-family HTML fixtures and golden extracted blocks; ruff; lizard complexity gate  
**Target Platform**: Local developer workstation and trusted local/internal service runtime  
**Project Type**: Python package with CLI, HTTP API, MCP server, ingestion services, and persistence adapters  
**Performance Goals**: Validate the complete manifest before network access; process every enabled source in one invocation; avoid fetching any source more than once per run; report every manifest entry even when individual sources fail  
**Constraints**: Cyclomatic complexity must remain 3 or below per function; no link crawling; nested content must not be omitted or duplicated; code layout must survive extraction; successful active content must survive failed refreshes; existing single-URL ingestion and search contracts remain usable  
**Scale/Scope**: One curated Go corpus containing seven initial public pages, with tens of future reviewed entries; sequential ingestion is sufficient for this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Complexity Under Four**: PASS. DOM selection, block classification, inline rendering, code rendering, manifest validation, entry execution, and result aggregation are separate helpers or collaborators. The corpus runner delegates one entry at a time and does not combine validation, fetching, and error classification in one function.
- **SOLID Design**: PASS. `PageExtractor`, `ManifestLoader`, and `SourceIngestor` boundaries each have one reason to change. The existing `IngestionPipeline` remains the stable single-source operation; corpus ingestion composes it instead of embedding manifest rules into it.
- **Separation of Concerns**: PASS. Checked-in configuration defines approved sources; manifest parsing validates configuration; DOM extraction produces blocks; the existing chunking/embedding/persistence path handles successful documents; corpus orchestration owns iteration and reporting; CLI code only adapts arguments and output.
- **Testable Agent-Facing Behavior**: PASS. Golden extraction tests cover every source family, integration tests prove only manifest URLs are fetched, contract tests cover additive provenance fields, and search tests prove every result maps to its stable corpus source.
- **Explicit Boundaries**: PASS. The versioned manifest schema, corpus-run output, new optional document provenance fields, additive HTTP/MCP search metadata, and database migration are documented. Single-URL documents retain null corpus metadata.

## Project Structure

### Documentation (this feature)

```text
specs/003-go-corpus-extraction/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- corpus-manifest.schema.json
|   |-- corpus-ingestion.md
|   `-- retrieval-provenance.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/net2vec/
|-- cli/
|   `-- ingest_corpus.py
|-- config/
|   `-- corpora/
|       `-- go-style.json
|-- domain/
|   |-- corpus.py
|   `-- documents.py
|-- ingestion/
|   |-- corpus.py
|   |-- extractor.py
|   |-- manifest.py
|   `-- pipeline.py
|-- persistence/
|   |-- migrations/versions/0002_add_corpus_provenance.py
|   |-- models.py
|   `-- repositories.py
|-- api/routes.py
`-- mcp/server.py

tests/
|-- contract/
|   |-- test_corpus_manifest_contract.py
|   |-- test_http_search_contract.py
|   `-- test_mcp_search_docs_contract.py
|-- fixtures/
|   `-- extraction/
|       |-- google_style.html
|       |-- go_dev_guide.html
|       `-- expected_blocks.json
|-- integration/
|   |-- test_corpus_ingestion_flow.py
|   `-- test_search_flow.py
`-- unit/
    |-- test_corpus_manifest.py
    |-- test_corpus_runner.py
    `-- test_extractor.py
```

**Structure Decision**: Extend the existing single Python package. The current single-URL pipeline remains the unit of work. New domain and ingestion modules represent and orchestrate a corpus without moving embedding, persistence, retrieval, HTTP, or MCP responsibilities across their established boundaries.

## Complexity Tracking

No constitution violations identified.

## Phase 0: Research Summary

Research output is captured in [research.md](./research.md). Key decisions:

- Use semantic DOM traversal through the existing BeautifulSoup/lxml dependencies instead of repairing the stateful single-buffer parser.
- Use top-level semantic blocks plus dedicated renderers for inline text, code, lists, and tables to prevent nested duplication.
- Store the curated corpus as a versioned, checked-in JSON manifest validated in full before any fetch.
- Keep the seven official URLs explicit and never crawl links.
- Compose the existing per-URL pipeline in a sequential corpus runner with one outcome per manifest entry and failure isolation.
- Persist optional stable corpus/source provenance and expose it additively through search contracts.
- Replace the current URL/active uniqueness constraint with active-only uniqueness so repeated corpus refreshes can retain more than one inactive historical record.

## Phase 1: Design Summary

Design output is captured in [data-model.md](./data-model.md), [quickstart.md](./quickstart.md), and [contracts/](./contracts/).

### Post-Design Constitution Check

- **Complexity Under Four**: PASS. The design assigns selection, rendering, validation, execution, and outcome mapping to independent operations. Table-driven dispatch replaces multi-branch element handling where practical.
- **SOLID Design**: PASS. Protocol boundaries allow fake extractors, loaders, and per-source ingestors in tests. Corpus orchestration extends the system by composition without modifying search or embedding behavior.
- **Separation of Concerns**: PASS. Manifest data, validation, extraction, chunking, embedding, persistence, reporting, and entry-point formatting have distinct owners.
- **Testable Agent-Facing Behavior**: PASS. The contract set defines manifest validity, run outcomes, and provenance fields; fixtures and integration scenarios directly validate what agents can retrieve and trust.
- **Explicit Boundaries**: PASS. Migration defaults preserve existing rows, manifest versioning supports future evolution, and added response fields are optional for legacy single-URL content.

