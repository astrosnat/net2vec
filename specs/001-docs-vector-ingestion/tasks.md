---
description: "Task list for Documentation Vector Ingestion"
---

# Tasks: Documentation Vector Ingestion

**Input**: Design documents from `/specs/001-docs-vector-ingestion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included because the specification requires independently
testable increments, contract validation, and end-to-end validation.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single Python project: `src/net2vec/`, `tests/`, `specs/001-docs-vector-ingestion/`
- Contract files: `specs/001-docs-vector-ingestion/contracts/`
- Configuration examples: `config/` and generated snippets documented in `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python project, dependency metadata, quality gates,
and package skeleton.

- [ ] T001 Create Python package directories and `__init__.py` files under `src/net2vec/api`, `src/net2vec/cli`, `src/net2vec/config`, `src/net2vec/domain`, `src/net2vec/ingestion`, `src/net2vec/embeddings`, `src/net2vec/persistence`, `src/net2vec/search`, and `src/net2vec/mcp`
- [ ] T002 Create test directories `tests/unit`, `tests/contract`, and `tests/integration` with package markers where needed
- [ ] T003 Create `pyproject.toml` with Python 3.12 metadata and dependencies FastAPI, Uvicorn, Typer, Pydantic, SQLAlchemy 2.x, Alembic, psycopg, pgvector, OpenAI, BeautifulSoup4, lxml, httpx, MCP Python SDK, pytest, ruff, and lizard
- [ ] T004 Configure ruff and pytest options in `pyproject.toml`
- [ ] T005 Configure lizard complexity gate command in `pyproject.toml` or `scripts/check-complexity.ps1`
- [ ] T006 [P] Create `.env.example` documenting `DATABASE_URL`, `OPENAI_API_KEY`, `NET2VEC_EMBEDDING_MODEL`, `NET2VEC_API_HOST`, `NET2VEC_API_PORT`, and `NET2VEC_MCP_URL`
- [ ] T007 [P] Update `README.md` with local setup commands and links to `specs/001-docs-vector-ingestion/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration, database, domain contracts, and infrastructure
that MUST be complete before any user story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T008 Implement settings loading in `src/net2vec/config/settings.py`
- [ ] T009 Create domain models for `SourceDocument`, `DocumentSection`, `SearchQuery`, and `SearchResult` in `src/net2vec/domain/documents.py`, `src/net2vec/domain/chunks.py`, and `src/net2vec/domain/search.py`
- [ ] T010 Implement database engine/session setup in `src/net2vec/persistence/database.py`
- [ ] T011 Create SQLAlchemy persistence models with pgvector fields in `src/net2vec/persistence/models.py`
- [ ] T012 Create initial Alembic environment and migration enabling pgvector in `src/net2vec/persistence/migrations`
- [ ] T013 Implement repository interfaces and SQLAlchemy repository stubs in `src/net2vec/persistence/repositories.py`
- [ ] T014 [P] Implement shared error types and result objects in `src/net2vec/domain/documents.py` and `src/net2vec/domain/search.py`
- [ ] T015 [P] Implement embedding client interface and OpenAI embedding adapter skeleton in `src/net2vec/embeddings/client.py`
- [ ] T016 [P] Implement API application factory and health route in `src/net2vec/api/app.py`
- [ ] T017 [P] Implement Typer CLI root wiring in `src/net2vec/cli/__init__.py`
- [ ] T018 [P] Implement MCP server bootstrap skeleton in `src/net2vec/mcp/server.py`
- [ ] T019 Verify SOLID boundaries and no business rules in adapters across `src/net2vec/api`, `src/net2vec/cli`, and `src/net2vec/mcp`

**Checkpoint**: Foundation ready. Database schema, settings, domain models, and
adapter skeletons exist; user story work can begin.

---

## Phase 3: User Story 1 - Ingest a Documentation Page (Priority: P1) MVP

**Goal**: A developer can ingest one exact documentation URL, store heading-aware
chunks, and refresh the URL by replacing previous active content.

**Independent Test**: Provide a public documentation URL, run ingestion, and
verify the corpus records one active source document with title, URL, heading
structure, searchable chunks, and replacement-on-refresh behavior.

### Tests for User Story 1

- [ ] T020 [P] [US1] Add unit tests for exact URL validation and no-crawl behavior in `tests/unit/test_ingest_url_policy.py`
- [ ] T021 [P] [US1] Add unit tests for boilerplate removal and title extraction in `tests/unit/test_extractor.py`
- [ ] T022 [P] [US1] Add unit tests for heading-aware chunk creation and no-heading fallback in `tests/unit/test_chunker.py`
- [ ] T023 [P] [US1] Add unit tests for embedding batching and model dimension validation in `tests/unit/test_embedding_service.py`
- [ ] T024 [P] [US1] Add repository tests for one-active-version refresh semantics in `tests/unit/test_repositories.py`
- [ ] T025 [US1] Add integration test for first ingest and refresh replacement flow in `tests/integration/test_ingest_refresh_flow.py`

### Implementation for User Story 1

- [ ] T026 [US1] Implement exact HTTP/HTTPS URL validation in `src/net2vec/ingestion/fetcher.py`
- [ ] T027 [US1] Implement single-page HTTP fetching with timeout, redirect limit, and unsupported-content errors in `src/net2vec/ingestion/fetcher.py`
- [ ] T028 [US1] Implement HTML content extraction, title extraction, and boilerplate cleanup in `src/net2vec/ingestion/extractor.py`
- [ ] T029 [US1] Implement heading-aware section traversal and fallback heading path behavior in `src/net2vec/ingestion/chunker.py`
- [ ] T030 [US1] Implement excerpt creation, token counting, source order, and chunk hashing in `src/net2vec/ingestion/chunker.py`
- [ ] T031 [US1] Implement OpenAI embedding generation service with configured model and dimension checks in `src/net2vec/embeddings/service.py`
- [ ] T032 [US1] Implement repository method to replace active chunks for a source URL transactionally in `src/net2vec/persistence/repositories.py`
- [ ] T033 [US1] Implement ingestion orchestration pipeline in `src/net2vec/ingestion/pipeline.py`
- [ ] T034 [US1] Implement CLI command `python -m net2vec.cli.ingest <url>` in `src/net2vec/cli/ingest.py`
- [ ] T035 [US1] Add structured ingestion logs without leaking secrets in `src/net2vec/ingestion/pipeline.py`
- [ ] T036 [US1] Verify US1 functions stay below cyclomatic complexity 4 with `lizard -C 3 src/net2vec/ingestion src/net2vec/embeddings src/net2vec/persistence tests`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Search Ingested Documentation (Priority: P2)

**Goal**: A developer or agent can search active ingested documentation and get
ranked results containing excerpt, full chunk, source URL, heading context, rank,
and score.

**Independent Test**: Ask a style-guide question whose answer appears in an
ingested page and verify relevant sections are returned first, with clear
no-match behavior for unrelated queries.

### Tests for User Story 2

- [ ] T037 [P] [US2] Add contract tests for `/search` request and response shape from `contracts/openapi.yaml` in `tests/contract/test_http_search_contract.py`
- [ ] T038 [P] [US2] Add unit tests for search query validation and limit bounds in `tests/unit/test_search_service.py`
- [ ] T039 [P] [US2] Add unit tests for ranking output and active-section filtering in `tests/unit/test_search_service.py`
- [ ] T040 [P] [US2] Add unit tests for no-match and empty-corpus responses in `tests/unit/test_search_service.py`
- [ ] T041 [US2] Add integration test for ingest then semantic search flow in `tests/integration/test_search_flow.py`

### Implementation for User Story 2

- [ ] T042 [US2] Implement search request and result schemas in `src/net2vec/api/routes.py`
- [ ] T043 [US2] Implement query embedding reuse through `src/net2vec/embeddings/service.py`
- [ ] T044 [US2] Implement pgvector similarity search over active chunks in `src/net2vec/search/service.py`
- [ ] T045 [US2] Implement relevance rank and score normalization in `src/net2vec/search/ranking.py`
- [ ] T046 [US2] Implement `/search` route with clear no-match and validation responses in `src/net2vec/api/routes.py`
- [ ] T047 [US2] Wire search routes into FastAPI application in `src/net2vec/api/app.py`
- [ ] T048 [US2] Add `/ingest` HTTP route delegating to the US1 pipeline in `src/net2vec/api/routes.py`
- [ ] T049 [US2] Verify returned results include excerpt, full chunk, source URL, heading path, rank, and score in `src/net2vec/search/service.py`
- [ ] T050 [US2] Verify US2 functions stay below cyclomatic complexity 4 with `lizard -C 3 src/net2vec/search src/net2vec/api tests`

**Checkpoint**: User Stories 1 and 2 are independently functional; HTTP search
contract is valid.

---

## Phase 5: User Story 3 - Let Codex Query Documentation (Priority: P3)

**Goal**: Codex can connect to the local/internal MCP server and call
`search_docs` to retrieve the same source-grounded results as the HTTP search
service.

**Independent Test**: Configure Codex against the local MCP server, ask about an
ingested guide, and verify `search_docs` returns usable results or clear
diagnostics when unavailable.

### Tests for User Story 3

- [ ] T051 [P] [US3] Add MCP tool contract tests from `contracts/mcp-search-docs.json` in `tests/contract/test_mcp_search_docs_contract.py`
- [ ] T052 [P] [US3] Add unit tests for Codex config snippet generation in `tests/unit/test_codex_config.py`
- [ ] T053 [P] [US3] Add unit tests for MCP no-match and validation responses in `tests/unit/test_mcp_server.py`
- [ ] T054 [US3] Add integration test for Codex configuration quickstart expectations in `tests/integration/test_codex_config_quickstart.py`

### Implementation for User Story 3

- [ ] T055 [US3] Implement `search_docs` MCP tool input and output schemas in `src/net2vec/mcp/server.py`
- [ ] T056 [US3] Implement MCP `search_docs` handler delegating to `src/net2vec/search/service.py`
- [ ] T057 [US3] Implement MCP server startup on local/internal endpoint in `src/net2vec/mcp/server.py`
- [ ] T058 [US3] Implement Codex config snippet generation in `src/net2vec/config/codex.py`
- [ ] T059 [US3] Add CLI command to print Codex MCP config in `src/net2vec/cli/ingest.py` or a new `src/net2vec/cli/configure.py`
- [ ] T060 [US3] Update `specs/001-docs-vector-ingestion/quickstart.md` with exact MCP server startup and Codex validation commands from the implemented CLI
- [ ] T061 [US3] Verify MCP output includes excerpt, full chunk, source URL, heading path, rank, and score in `src/net2vec/mcp/server.py`
- [ ] T062 [US3] Verify US3 functions stay below cyclomatic complexity 4 with `lizard -C 3 src/net2vec/mcp src/net2vec/config tests`

**Checkpoint**: All user stories are independently functional; Codex can query
documentation through `search_docs`.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, performance checks, and quality
gates across all stories.

- [ ] T063 [P] Update `README.md` with the full ingest, search API, MCP, and Codex flow
- [ ] T064 [P] Add representative retrieval evaluation fixtures for Effective Go queries in `tests/fixtures/effective_go_queries.json`
- [ ] T065 Add retrieval quality test asserting known answers appear in top 3 for representative queries in `tests/integration/test_search_flow.py`
- [ ] T066 Add performance smoke test for one-page ingest under 2 minutes and small-corpus search under 2 seconds in `tests/integration/test_performance_smoke.py`
- [ ] T067 Run quickstart validation steps and record any required doc fixes in `specs/001-docs-vector-ingestion/quickstart.md`
- [ ] T068 Run full test suite with `pytest`
- [ ] T069 Run lint gate with `ruff check .`
- [ ] T070 Run complexity gate with `lizard -C 3 src tests`
- [ ] T071 Review changed modules for SOLID responsibilities and separation of concerns against `specs/001-docs-vector-ingestion/plan.md`
- [ ] T072 Confirm contracts in `specs/001-docs-vector-ingestion/contracts/openapi.yaml` and `specs/001-docs-vector-ingestion/contracts/mcp-search-docs.json` match implemented responses

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; establishes ingestable searchable data.
- **User Story 2 (Phase 4)**: Depends on US1 because search requires active chunks.
- **User Story 3 (Phase 5)**: Depends on US2 because MCP delegates to the shared search service.
- **Polish (Phase 6)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 - Ingest a Documentation Page**: MVP; no other story dependency after Foundation.
- **US2 - Search Ingested Documentation**: Requires US1 data model, chunks, embeddings, and repository refresh semantics.
- **US3 - Let Codex Query Documentation**: Requires US2 search service and result shape.

### Within Each User Story

- Tests are written before implementation tasks for that story.
- Domain and schema work precedes services.
- Services precede CLI, HTTP, or MCP adapters.
- Contract tests precede implementation of their external interface.
- Complexity verification closes each story.

### Parallel Opportunities

- Setup tasks T006-T007 can run in parallel after `pyproject.toml` decisions are known.
- Foundational skeleton tasks T014-T018 can run in parallel after domain and database setup begins.
- US1 test tasks T020-T024 can run in parallel.
- US2 test tasks T037-T040 can run in parallel after US1 is complete.
- US3 test tasks T051-T053 can run in parallel after US2 is complete.
- Polish documentation and fixture tasks T063-T064 can run in parallel.

---

## Parallel Example: User Story 1

```text
Task: "T020 [P] [US1] Add unit tests for exact URL validation and no-crawl behavior in tests/unit/test_ingest_url_policy.py"
Task: "T021 [P] [US1] Add unit tests for boilerplate removal and title extraction in tests/unit/test_extractor.py"
Task: "T022 [P] [US1] Add unit tests for heading-aware chunk creation and no-heading fallback in tests/unit/test_chunker.py"
Task: "T023 [P] [US1] Add unit tests for embedding batching and model dimension validation in tests/unit/test_embedding_service.py"
Task: "T024 [P] [US1] Add repository tests for one-active-version refresh semantics in tests/unit/test_repositories.py"
```

## Parallel Example: User Story 2

```text
Task: "T037 [P] [US2] Add contract tests for /search request and response shape from contracts/openapi.yaml in tests/contract/test_http_search_contract.py"
Task: "T038 [P] [US2] Add unit tests for search query validation and limit bounds in tests/unit/test_search_service.py"
Task: "T039 [P] [US2] Add unit tests for ranking output and active-section filtering in tests/unit/test_search_service.py"
Task: "T040 [P] [US2] Add unit tests for no-match and empty-corpus responses in tests/unit/test_search_service.py"
```

## Parallel Example: User Story 3

```text
Task: "T051 [P] [US3] Add MCP tool contract tests from contracts/mcp-search-docs.json in tests/contract/test_mcp_search_docs_contract.py"
Task: "T052 [P] [US3] Add unit tests for Codex config snippet generation in tests/unit/test_codex_config.py"
Task: "T053 [P] [US3] Add unit tests for MCP no-match and validation responses in tests/unit/test_mcp_server.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational prerequisites.
3. Complete Phase 3: User Story 1.
4. Stop and validate exact-URL ingestion, heading-aware chunks, embeddings, and refresh replacement.

### Incremental Delivery

1. Deliver US1 to create a searchable corpus.
2. Deliver US2 to search the corpus through HTTP.
3. Deliver US3 to expose the same search behavior through MCP for Codex.
4. Finish Polish gates and documentation.

### Validation Gates

1. Run `pytest` after each story checkpoint.
2. Run `ruff check .` before merging each story.
3. Run `lizard -C 3 src tests` before merging each story.
4. Confirm contract files match implemented HTTP and MCP responses before final delivery.

---

## Notes

- `[P]` tasks use different files and have no dependency on incomplete tasks in the same phase.
- `[Story]` labels map tasks to specific user stories for traceability.
- Tasks preserve the constitution's complexity, SOLID, separation-of-concerns, and boundary-validation requirements.
- Avoid adding crawler behavior, public authentication, Claude configuration, or historical version retention in this feature.
