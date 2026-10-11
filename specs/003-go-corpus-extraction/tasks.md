# Tasks: Go Corpus Extraction

**Input**: Design documents from `/specs/003-go-corpus-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the specification for extraction regressions, manifest validation, corpus failure isolation, provenance contracts, and independently testable user stories.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated as a distinct increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes different files and has no dependency on another incomplete task in the same group
- **[Story]**: Maps the task to a user story from spec.md
- Every task names the exact file or directory it changes

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish checked-in configuration and regression-fixture locations used by later phases.

- [x] T001 Create the corpus configuration package markers in `src/net2vec/config/corpora/__init__.py`
- [x] T002 [P] Create extraction fixture directories and document fixture provenance in `tests/fixtures/extraction/README.md`
- [x] T003 [P] Register the `net2vec-ingest-corpus` console command target in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared domain contracts and persistence compatibility required by corpus execution and provenance reporting.

**CRITICAL**: Complete this phase before beginning story implementation.

- [x] T004 Create typed corpus manifest, source, outcome, run, and status domain models with boundary validation in `src/net2vec/domain/corpus.py`
- [x] T005 Extend source document domain and search match/result models with optional corpus provenance and resolved URL fields in `src/net2vec/domain/documents.py` and `src/net2vec/domain/search.py`
- [x] T006 Add nullable corpus provenance and resolved URL columns and replace `(source_url, active)` uniqueness with active-only source URL uniqueness in `src/net2vec/persistence/migrations/versions/0002_add_corpus_provenance.py`
- [x] T007 Align SQLAlchemy document fields and active-only index metadata with the migration in `src/net2vec/persistence/models.py`
- [x] T008 Update document record mapping and search-result mapping to preserve optional provenance in `src/net2vec/persistence/repositories.py`
- [x] T009 [P] Add migration and model schema tests for nullable provenance and repeatable inactive history in `tests/unit/test_corpus_storage_schema.py`
- [x] T010 [P] Add domain validation tests for corpus identifiers, classifications, outcome counts, and provenance invariants in `tests/unit/test_corpus_domain.py`

**Checkpoint**: Shared corpus and provenance boundaries are explicit, migrated, and testable.

---

## Phase 3: User Story 1 - Preserve Style Guidance Accurately (Priority: P1) MVP

**Goal**: Extract prose, inline identifiers, headings, lists, tables, links, labels, and preformatted Go examples in reading order without omission or duplication.

**Independent Test**: Run extraction tests against representative Google Style and go.dev fixtures and compare every emitted block with golden expected content, including nested inline code and multiline examples.

### Tests for User Story 1

- [x] T011 [P] [US1] Add representative nested markup from Google Style pages to `tests/fixtures/extraction/google_style.html`
- [x] T012 [P] [US1] Add representative nested markup from go.dev guides and wiki pages to `tests/fixtures/extraction/go_dev_guide.html`
- [x] T013 [P] [US1] Define ordered golden block output for both source families in `tests/fixtures/extraction/expected_blocks.json`
- [x] T014 [US1] Add failing fixture-driven tests for reading order, no duplication, code whitespace, lists, tables, labels, links, boilerplate removal, and empty pages in `tests/unit/test_extractor.py`

### Implementation for User Story 1

- [x] T015 [US1] Replace the single-buffer parser with primary-content DOM selection and excluded-element removal in `src/net2vec/ingestion/extractor.py`
- [x] T016 [US1] Implement outermost semantic block selection and inline text rendering without nested duplication in `src/net2vec/ingestion/extractor.py`
- [x] T017 [US1] Implement dedicated preformatted code, list item, and table row rendering with kind-appropriate whitespace preservation in `src/net2vec/ingestion/extractor.py`
- [x] T018 [US1] Reject pages with no meaningful extracted blocks before embedding or persistence in `src/net2vec/ingestion/pipeline.py`
- [x] T019 [US1] Update chunk construction to retain the expanded extracted block kinds and code boundaries in `src/net2vec/ingestion/chunker.py`
- [x] T020 [US1] Run the extraction regression suite and refactor changed functions to cyclomatic complexity 3 or below in `src/net2vec/ingestion/extractor.py` and `src/net2vec/ingestion/chunker.py`

**Checkpoint**: User Story 1 is independently complete and constitutes the MVP.

---

## Phase 4: User Story 2 - Ingest the Curated Go Corpus (Priority: P2)

**Goal**: Validate and ingest the seven-source approved Go corpus without crawling, while isolating source failures and reporting every entry.

**Independent Test**: Run corpus ingestion with fake fetch/embedding/storage boundaries and verify each enabled URL is processed exactly once, disabled entries are skipped, unlisted links are ignored, partial failures preserve successes, and invalid manifests cause zero fetches.

### Tests for User Story 2

- [x] T021 [P] [US2] Add a contract test that validates default manifest shape and all seven approved entries against `specs/003-go-corpus-extraction/contracts/corpus-manifest.schema.json` in `tests/contract/test_corpus_manifest_contract.py`
- [x] T022 [P] [US2] Add unit tests for malformed JSON, unsupported schema versions, missing fields, duplicate IDs, normalized duplicate URLs, invalid classifications, and no enabled sources in `tests/unit/test_corpus_manifest.py`
- [x] T023 [P] [US2] Add unit tests for ordered execution, disabled entries, per-source failure isolation, complete outcome counts, and sanitized messages in `tests/unit/test_corpus_runner.py`
- [x] T024 [US2] Add an integration test proving only enabled manifest URLs are fetched and successful sources remain active after another source fails in `tests/integration/test_corpus_ingestion_flow.py`

### Implementation for User Story 2

- [x] T025 [P] [US2] Create the versioned seven-source allowlist in `src/net2vec/config/corpora/go-style.json`
- [x] T026 [US2] Implement JSON loading, schema-version checks, URL normalization, cross-entry validation, and fail-before-fetch behavior in `src/net2vec/ingestion/manifest.py`
- [x] T027 [US2] Extend single-source ingestion to accept optional manifest provenance while keeping legacy URL ingestion compatible in `src/net2vec/ingestion/pipeline.py`
- [x] T028 [US2] Implement sequential corpus orchestration, skipped outcomes, per-source error isolation, and aggregate counts in `src/net2vec/ingestion/corpus.py`
- [x] T029 [US2] Implement default/custom manifest selection, per-entry output, summary output, and exit codes 0/1/2 in `src/net2vec/cli/ingest_corpus.py`
- [x] T030 [US2] Add CLI tests for default manifest use, custom manifest selection, output ordering, and success/partial-failure/validation exit codes in `tests/unit/test_ingest_corpus_cli.py`
- [x] T031 [US2] Verify no-crawl behavior, SOLID boundaries, sanitized failures, and cyclomatic complexity 3 or below across `src/net2vec/ingestion/manifest.py`, `src/net2vec/ingestion/corpus.py`, and `src/net2vec/cli/ingest_corpus.py`

**Checkpoint**: User Stories 1 and 2 work together, while corpus validation and orchestration remain independently testable through injected boundaries.

---

## Phase 5: User Story 3 - Review Corpus Coverage and Provenance (Priority: P3)

**Goal**: Make corpus coverage and stable source provenance visible in run results and every retrieved manifest-backed section.

**Independent Test**: Ingest a manifest-backed source, search for one of its sections, and verify the run and result identify the corpus, manifest source, classification, reviewed URL, resolved URL, heading path, content hash, and terminal outcome.

### Tests for User Story 3

- [ ] T032 [P] [US3] Extend HTTP contract tests for optional corpus provenance and legacy null compatibility in `tests/contract/test_http_search_contract.py`
- [ ] T033 [P] [US3] Extend MCP contract tests for optional corpus provenance and legacy result compatibility in `tests/contract/test_mcp_search_docs_contract.py`
- [ ] T034 [P] [US3] Add repository mapping tests for manifest provenance, resolved redirects, and stable source identity across refreshes in `tests/unit/test_repositories.py`
- [ ] T035 [US3] Extend search integration coverage from manifest ingestion through provenance-bearing retrieval in `tests/integration/test_search_flow.py`

### Implementation for User Story 3

- [ ] T036 [US3] Preserve submitted source URL and final resolved URL separately when creating manifest-backed source documents in `src/net2vec/ingestion/pipeline.py`
- [ ] T037 [US3] Propagate corpus ID, manifest source ID, classification, and resolved URL through search ranking in `src/net2vec/search/ranking.py`
- [ ] T038 [US3] Add optional provenance fields to HTTP search response models and mappings in `src/net2vec/api/routes.py`
- [ ] T039 [US3] Add optional provenance fields to MCP tool output schema and payload mapping in `src/net2vec/mcp/server.py`
- [ ] T040 [US3] Verify additive contract compatibility, complete traceability, SOLID responsibilities, and cyclomatic complexity 3 or below across retrieval and agent-facing modules in `src/net2vec/search/ranking.py`, `src/net2vec/api/routes.py`, and `src/net2vec/mcp/server.py`

**Checkpoint**: All three user stories are functional and every manifest-backed retrieval result is traceable to reviewed corpus configuration.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, acceptance validation, and repository-wide quality gates.

- [ ] T041 [P] Document curated corpus ingestion, manifest maintenance, partial-failure semantics, and provenance fields in `README.md`
- [ ] T042 [P] Update environment and operational examples if needed for corpus ingestion in `.env.example`
- [ ] T043 Execute every command and scenario in `specs/003-go-corpus-extraction/quickstart.md` and correct documentation discrepancies in that file
- [ ] T044 Run `python -m pytest -ra` and resolve regressions across `tests/`
- [ ] T045 Run `python -m ruff check .` and resolve lint failures across `src/` and `tests/`
- [ ] T046 Run `python -m lizard -C 3 src tests` and refactor every function or method exceeding cyclomatic complexity 3 in `src/` and `tests/`
- [ ] T047 Review manifest, migration, extraction, persistence, retrieval, HTTP, and MCP boundaries against `specs/003-go-corpus-extraction/contracts/` and record final compliance in `specs/003-go-corpus-extraction/checklists/requirements.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on Setup and blocks all story phases.
- **User Story 1 (Phase 3)**: Starts after Foundational and delivers the extraction MVP.
- **User Story 2 (Phase 4)**: Starts after Foundational; manifest and runner work can proceed against the extraction contract, but end-to-end acceptance uses completed US1 extraction.
- **User Story 3 (Phase 5)**: Starts after Foundational; contract/model work can proceed in parallel, but its end-to-end test depends on US2 manifest ingestion.
- **Polish (Phase 6)**: Depends on every story selected for delivery.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1 (accurate extraction) ---------+
                    -> US2 (corpus ingestion) ------------+-> US3 (retrieval provenance)
                                                         +-> Polish
```

- **US1** has no dependency on another user story.
- **US2** is independently testable with an injected single-source ingestor; integrated corpus acceptance includes US1.
- **US3** contract and mapping work is independently testable; its complete user journey consumes US2 output.

### Within Each User Story

- Write the listed tests first and confirm they fail for the missing behavior.
- Define or extend domain contracts before services that consume them.
- Implement core behavior before CLI, HTTP, or MCP adapters.
- Complete the story checkpoint before treating the increment as deliverable.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 begins.
- T009 and T010 can run in parallel after their corresponding foundational models are defined.
- T011, T012, and T013 can be prepared in parallel before T014.
- T021, T022, and T023 can be written in parallel; T025 can also proceed independently.
- T032, T033, and T034 can be written in parallel.
- T041 and T042 can run in parallel after story behavior stabilizes.
- After Foundation, separate contributors can work on US1 fixtures/extraction, US2 manifest contracts, and US3 response contract tests, respecting the integration dependencies above.

---

## Parallel Example: User Story 1

```text
Task T011: Add Google Style extraction fixture in tests/fixtures/extraction/google_style.html
Task T012: Add go.dev extraction fixture in tests/fixtures/extraction/go_dev_guide.html
Task T013: Define golden block output in tests/fixtures/extraction/expected_blocks.json
```

## Parallel Example: User Story 2

```text
Task T021: Add manifest schema contract test in tests/contract/test_corpus_manifest_contract.py
Task T022: Add invalid-manifest unit tests in tests/unit/test_corpus_manifest.py
Task T023: Add corpus runner unit tests in tests/unit/test_corpus_runner.py
Task T025: Create the approved manifest in src/net2vec/config/corpora/go-style.json
```

## Parallel Example: User Story 3

```text
Task T032: Extend HTTP search contract tests in tests/contract/test_http_search_contract.py
Task T033: Extend MCP search contract tests in tests/contract/test_mcp_search_docs_contract.py
Task T034: Add persistence provenance mapping tests in tests/unit/test_repositories.py
```

---

## Implementation Strategy

### MVP First: User Story 1

1. Complete Setup and Foundation.
2. Write the real-structure extraction fixtures and golden assertions.
3. Replace the extractor and update chunk handling.
4. Stop and validate US1 independently before adding corpus orchestration.

### Incremental Delivery

1. **MVP**: Accurate extraction prevents corrupt or incomplete retrieval content.
2. **Corpus increment**: The reviewed seven-source manifest and isolated ingestion fill the approved corpus.
3. **Trust increment**: Provenance and coverage reporting let maintainers and agents verify retrieved guidance.
4. **Polish**: Run the documented workflow and all quality/constitution gates.

### Parallel Team Strategy

1. Complete Setup and Foundation together.
2. Assign extraction fixtures and extractor work to one contributor.
3. Assign manifest schema, loader, and runner tests to a second contributor using injected boundaries.
4. Assign provenance contract tests and migration review to a third contributor.
5. Integrate in priority order: US1, US2, US3, then run all cross-cutting gates.

## Notes

- `[P]` means the task changes different files and can proceed without an incomplete dependency.
- `[US1]`, `[US2]`, and `[US3]` provide direct traceability to specification stories.
- Tests precede implementation within each story because acceptance and regression validation are explicit feature requirements.
- Do not introduce crawling, scheduled refresh, source precedence, generation orchestration, or unrestricted user-provided corpus URLs in this feature.
- Preserve unrelated working-tree changes and commit only when explicitly requested.
