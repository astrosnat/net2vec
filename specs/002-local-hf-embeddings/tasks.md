# Tasks: Local Embedding Provider

**Input**: Design documents from `/specs/002-local-hf-embeddings/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included because the feature specification requires independently executable validation and the plan calls out factory, local embedding, storage, HTTP, MCP, and integration behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependency and example configuration support for local embeddings.

- [ ] T001 Add `torch` and `transformers` runtime dependencies in `pyproject.toml`
- [ ] T002 Add `NET2VEC_EMBEDDING_PROVIDER=local`, `NET2VEC_EMBEDDING_MODEL=microsoft/codebert-base`, and `NET2VEC_EMBEDDING_DIMENSIONS=768` defaults in `.env.example`
- [ ] T003 [P] Update local embedding setup notes in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Centralize provider selection and configuration before user story work begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add `embedding_provider` to `Settings` and default local model/dimension values in `src/net2vec/config/settings.py`
- [ ] T005 Add provider validation helpers for `local` and `openai` values in `src/net2vec/config/settings.py`
- [ ] T006 [P] Create embedding provider factory skeleton in `src/net2vec/embeddings/factory.py`
- [ ] T007 Update imports and default embedding service construction to call the factory in `src/net2vec/cli/ingest.py`
- [ ] T008 Update imports and default embedding service construction to call the factory in `src/net2vec/api/routes.py`
- [ ] T009 Update imports and default embedding service construction to call the factory in `src/net2vec/mcp/server.py`
- [ ] T010 [P] Add settings default and provider validation tests in `tests/unit/test_settings.py`
- [ ] T011 [P] Add factory selection tests with fake clients in `tests/unit/test_embedding_factory.py`
- [ ] T012 Run `pytest tests/unit/test_settings.py tests/unit/test_embedding_factory.py -ra` and confirm new foundational tests fail before implementation is complete

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Run Without Paid Embedding API (Priority: P1) MVP

**Goal**: Developers can ingest and search documentation with local embeddings and no external embedding API key.

**Independent Test**: Clear `OPENAI_API_KEY`, set provider to `local`, ingest one documentation page, and search stored chunks.

### Tests for User Story 1

- [ ] T013 [P] [US1] Add local embedding client unit tests with mocked tokenizer/model outputs in `tests/unit/test_local_embedding_client.py`
- [ ] T014 [P] [US1] Add local no-API-key ingestion integration test using a fake local client through the factory boundary in `tests/integration/test_local_embedding_flow.py`
- [ ] T015 [P] [US1] Add local query embedding reuse test in `tests/unit/test_embedding_service.py`

### Implementation for User Story 1

- [ ] T016 [US1] Implement `LocalEmbeddingClient` loading tokenizer/model once and running eval/inference mode in `src/net2vec/embeddings/client.py`
- [ ] T017 [US1] Implement masked mean pooling and vector normalization helpers for local embeddings in `src/net2vec/embeddings/client.py`
- [ ] T018 [US1] Wire `local` provider creation to `LocalEmbeddingClient` in `src/net2vec/embeddings/factory.py`
- [ ] T019 [US1] Ensure local provider ignores missing `OPENAI_API_KEY` and returns 768-dimensional vectors in `src/net2vec/embeddings/factory.py`
- [ ] T020 [US1] Preserve OpenAI provider creation for explicit external mode in `src/net2vec/embeddings/factory.py`
- [ ] T021 [US1] Run `pytest tests/unit/test_local_embedding_client.py tests/unit/test_embedding_service.py tests/integration/test_local_embedding_flow.py -ra`
- [ ] T022 [US1] Run `lizard -C 3 src/net2vec/embeddings src/net2vec/config tests/unit/test_local_embedding_client.py tests/integration/test_local_embedding_flow.py`

**Checkpoint**: User Story 1 is functional and testable independently.

---

## Phase 4: User Story 2 - Select Embedding Mode From Configuration (Priority: P2)

**Goal**: CLI ingestion, HTTP search, and MCP search all use the same configured provider, and invalid provider configuration fails early.

**Independent Test**: Change `NET2VEC_EMBEDDING_PROVIDER` and verify CLI, HTTP, and MCP entry points use the selected mode or fail before work begins.

### Tests for User Story 2

- [ ] T023 [P] [US2] Add unsupported provider configuration test in `tests/unit/test_embedding_factory.py`
- [ ] T024 [P] [US2] Add OpenAI provider missing-key validation test in `tests/unit/test_embedding_factory.py`
- [ ] T025 [P] [US2] Add HTTP search invalid embedding configuration contract test in `tests/contract/test_http_search_contract.py`
- [ ] T026 [P] [US2] Add MCP search invalid embedding configuration contract test in `tests/contract/test_mcp_search_docs_contract.py`

### Implementation for User Story 2

- [ ] T027 [US2] Introduce a shared embedding configuration error type in `src/net2vec/embeddings/factory.py`
- [ ] T028 [US2] Map embedding configuration errors to 400-class HTTP responses in `src/net2vec/api/routes.py`
- [ ] T029 [US2] Surface embedding configuration errors without partial results in `src/net2vec/mcp/server.py`
- [ ] T030 [US2] Ensure CLI ingestion exits non-zero with clear provider/key errors in `src/net2vec/cli/ingest.py`
- [ ] T031 [US2] Run `pytest tests/unit/test_embedding_factory.py tests/contract/test_http_search_contract.py tests/contract/test_mcp_search_docs_contract.py -ra`
- [ ] T032 [US2] Run `lizard -C 3 src/net2vec/api src/net2vec/cli src/net2vec/mcp src/net2vec/embeddings tests/contract`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Keep Stored Vectors Compatible (Priority: P3)

**Goal**: Fresh database storage matches the configured local vector dimension, and dimension mismatches fail clearly.

**Independent Test**: Prepare a fresh database, ingest content with local mode, confirm stored vector metadata reports 768 dimensions, and verify mismatched dimensions are rejected.

### Tests for User Story 3

- [ ] T033 [P] [US3] Add model/migration vector dimension alignment test in `tests/unit/test_vector_storage_schema.py`
- [ ] T034 [P] [US3] Add repository or ingestion test asserting stored local metadata dimension is 768 in `tests/integration/test_local_embedding_flow.py`
- [ ] T035 [P] [US3] Add configured dimension mismatch test in `tests/unit/test_embedding_service.py`

### Implementation for User Story 3

- [ ] T036 [US3] Change SQLAlchemy document-section vector column to `Vector(768)` in `src/net2vec/persistence/models.py`
- [ ] T037 [US3] Change initial Alembic document-section vector column to `Vector(768)` in `src/net2vec/persistence/migrations/versions/0001_enable_pgvector.py`
- [ ] T038 [US3] Confirm embedding metadata records model and 768 dimensions during ingestion in `src/net2vec/ingestion/pipeline.py`
- [ ] T039 [US3] Add clear vector dimension compatibility notes to `README.md`
- [ ] T040 [US3] Run `pytest tests/unit/test_vector_storage_schema.py tests/unit/test_embedding_service.py tests/integration/test_local_embedding_flow.py -ra`
- [ ] T041 [US3] Run `lizard -C 3 src/net2vec/persistence src/net2vec/ingestion tests/unit/test_vector_storage_schema.py tests/integration/test_local_embedding_flow.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate documentation, contracts, quality gates, and quickstart behavior across the feature.

- [ ] T042 [P] Update `specs/002-local-hf-embeddings/quickstart.md` if implementation commands or dependency names changed
- [ ] T043 [P] Update `specs/002-local-hf-embeddings/contracts/embedding-configuration.md` if final error behavior differs
- [ ] T044 [P] Update `specs/002-local-hf-embeddings/contracts/vector-storage.md` if migration guidance differs
- [ ] T045 Run `pytest -ra`
- [ ] T046 Run `ruff check .`
- [ ] T047 Run `lizard -C 3 src tests`
- [ ] T048 Validate quickstart commands in `specs/002-local-hf-embeddings/quickstart.md` against a fresh local configuration
- [ ] T049 Review changed modules for SOLID responsibilities, separated concerns, and explicit data/integration boundaries

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and provides the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can be developed after or alongside US1 once the factory boundary exists.
- **User Story 3 (Phase 5)**: Depends on Foundational completion; should be integrated after US1 so local vector output shape is known.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after Foundational.
- **User Story 2 (P2)**: Uses the shared factory boundary from Foundational and can validate both providers independently.
- **User Story 3 (P3)**: Uses US1 local vector dimensions and updates persistence schema compatibility.

### Parallel Opportunities

- T003 can run in parallel with dependency/config setup.
- T006, T010, and T011 can run in parallel after T004/T005 design direction is clear.
- T013, T014, and T015 can run in parallel because they target different test files.
- T023, T024, T025, and T026 can run in parallel because they target separate validation surfaces.
- T033, T034, and T035 can run in parallel because they test schema, integration metadata, and service validation separately.
- T042, T043, and T044 can run in parallel during polish.

---

## Parallel Example: User Story 1

```powershell
# Launch test-authoring work for User Story 1 together:
Task: "T013 [P] [US1] Add local embedding client unit tests with mocked tokenizer/model outputs in tests/unit/test_local_embedding_client.py"
Task: "T014 [P] [US1] Add local no-API-key ingestion integration test using a fake local client through the factory boundary in tests/integration/test_local_embedding_flow.py"
Task: "T015 [P] [US1] Add local query embedding reuse test in tests/unit/test_embedding_service.py"
```

---

## Parallel Example: User Story 2

```powershell
# Launch configuration contract tests together:
Task: "T023 [P] [US2] Add unsupported provider configuration test in tests/unit/test_embedding_factory.py"
Task: "T025 [P] [US2] Add HTTP search invalid embedding configuration contract test in tests/contract/test_http_search_contract.py"
Task: "T026 [P] [US2] Add MCP search invalid embedding configuration contract test in tests/contract/test_mcp_search_docs_contract.py"
```

---

## Parallel Example: User Story 3

```powershell
# Launch vector compatibility tests together:
Task: "T033 [P] [US3] Add model/migration vector dimension alignment test in tests/unit/test_vector_storage_schema.py"
Task: "T034 [P] [US3] Add repository or ingestion test asserting stored local metadata dimension is 768 in tests/integration/test_local_embedding_flow.py"
Task: "T035 [P] [US3] Add configured dimension mismatch test in tests/unit/test_embedding_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate local ingestion/search with no `OPENAI_API_KEY`.

### Incremental Delivery

1. Setup + Foundational establish the provider boundary.
2. US1 adds local embeddings and validates no-API-key operation.
3. US2 hardens provider selection and error behavior across CLI, HTTP, and MCP.
4. US3 aligns storage schema and vector compatibility.
5. Polish validates docs, contracts, tests, lint, and complexity.

### Quality Gates

- Every changed function or method must stay at cyclomatic complexity 3 or below.
- API, CLI, MCP, ingestion, search, and persistence boundaries must not take on model-specific behavior.
- Generated vectors must be validated before storage or search.
- HTTP and MCP contracts must remain compatible for successful searches.
