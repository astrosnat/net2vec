# Feature Specification: Local Embedding Provider

**Feature Branch**: `002-local-hf-embeddings`  
**Created**: 2026-06-01  
**Status**: Draft  
**Input**: User description: "Modify this repo for adding a local Hugging Face/PyTorch embedding client, choose it from settings, and fix the pgvector schema dimension"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Without Paid Embedding API (Priority: P1)

As a developer running net2vec locally, I want document ingestion and search-query embedding to work without providing a paid external embedding API key so that I can use the tool with only local compute.

**Why this priority**: This is the primary value of the feature and removes the current cost blocker for local experimentation.

**Independent Test**: Can be fully tested by clearing the external embedding API key, selecting the local embedding option, ingesting one documentation URL, and confirming the stored chunks include embeddings.

**Acceptance Scenarios**:

1. **Given** no external embedding API key is configured, **When** the developer runs ingestion with local embeddings selected, **Then** ingestion completes and stores embeddings for every generated chunk.
2. **Given** the local embedding option is selected, **When** the developer searches previously ingested content, **Then** the query is embedded locally and ranked results are returned.

---

### User Story 2 - Select Embedding Mode From Configuration (Priority: P2)

As a developer, I want one clear configuration setting that chooses between supported embedding modes so that local and external embedding behavior is predictable across CLI, API, and agent-tool entry points.

**Why this priority**: A single configuration boundary prevents one entry point from silently using a different embedding source than another.

**Independent Test**: Can be tested by changing the embedding mode setting and observing that ingestion, search API, and agent-tool search all use the selected mode.

**Acceptance Scenarios**:

1. **Given** local embedding mode is configured, **When** ingestion, HTTP search, and agent-tool search are executed, **Then** all three use local embeddings.
2. **Given** an unsupported embedding mode is configured, **When** any entry point starts, **Then** it fails before work begins with a clear configuration error.

---

### User Story 3 - Keep Stored Vectors Compatible (Priority: P3)

As a developer maintaining an existing local database, I want the stored vector dimension to match the configured embedding mode so that ingestion and search do not fail due to incompatible vector sizes.

**Why this priority**: Even with local embeddings available, the feature is unusable if stored vectors cannot accept the generated dimension.

**Independent Test**: Can be tested by preparing the database, ingesting content with the local mode, and confirming stored vector records have the configured dimension and can be searched.

**Acceptance Scenarios**:

1. **Given** a fresh database is prepared for local embeddings, **When** content is ingested, **Then** every stored vector matches the configured local embedding dimension.
2. **Given** stored vectors were created with one dimension, **When** the developer configures a different dimension, **Then** the system reports the mismatch clearly rather than storing incompatible data.

### Edge Cases

- Local model assets are unavailable or cannot be loaded.
- The selected embedding mode and configured dimension do not match.
- The external embedding mode is selected without an API key.
- Existing stored vectors were created with a different dimension than the current configuration.
- An ingestion batch contains zero chunks after parsing.
- A local embedding call returns fewer vectors than input texts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a local embedding mode for both document chunks and search queries without requiring an external embedding API key.
- **FR-002**: System MUST expose a single runtime setting that selects the embedding mode used by CLI ingestion, HTTP search, and agent-tool search.
- **FR-003**: System MUST preserve the existing external embedding mode for users who explicitly configure it with valid credentials.
- **FR-004**: System MUST validate the selected embedding mode before ingestion or search work begins.
- **FR-005**: System MUST validate that generated vectors match the configured embedding dimension before storing or searching with them.
- **FR-006**: System MUST prepare vector storage so that the supported local embedding dimension can be stored and searched.
- **FR-007**: System MUST report clear, actionable errors when the embedding mode, credentials, model availability, stored vector dimension, or generated vector dimension is invalid.
- **FR-008**: System MUST record enough embedding metadata with stored chunks to identify the mode, model identity, and vector dimension used to create them.
- **FR-009**: System MUST ensure search queries use embeddings compatible with the active stored content.
- **FR-010**: System MUST document the local embedding configuration and the database preparation expectations for developers.

### Quality & Boundary Requirements

- **QB-001**: Feature behavior MUST be expressible as independently testable increments.
- **QB-002**: Requirements MUST identify affected data schemas, integration contracts, or agent-facing behavior.
- **QB-003**: Requirements MUST flag any expected design pressure that could exceed cyclomatic complexity 3 per function or method.
- **QB-004**: The embedding selection boundary MUST remain shared across all entry points to avoid duplicated configuration decisions.
- **QB-005**: The vector storage dimension change MUST be explicit in migration and developer setup expectations.
- **QB-006**: The local embedding path MUST remain isolated from ingestion, search ranking, API routing, and agent-tool contracts so those components do not take on model-specific responsibility.

### Key Entities

- **Embedding Mode Configuration**: The selected embedding source, model identity, expected vector dimension, and any credentials required for that mode.
- **Document Section Vector**: The stored representation of a documentation chunk's semantic meaning, including dimension and embedding metadata.
- **Search Query Vector**: The runtime representation of a user's search query used for ranking against active document sections.
- **Vector Storage Schema**: The database contract that determines which vector dimensions can be stored and compared.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can ingest at least one documentation page and search it locally with no external embedding API key configured.
- **SC-002**: 100% of stored document-section vectors produced by the local mode match the configured local vector dimension.
- **SC-003**: CLI ingestion, HTTP search, and agent-tool search all use the same configured embedding mode in every validated run.
- **SC-004**: Invalid embedding configuration is reported before any document content is partially stored.
- **SC-005**: A fresh developer setup can complete database preparation, one-page ingestion, and one search query using local embeddings by following the project documentation.

## Assumptions

- Local embedding mode is intended for trusted local development and internal agent workflows, matching the existing access assumptions.
- Local embedding quality only needs to be sufficient for documentation retrieval, not a general-purpose semantic search benchmark.
- Existing external embedding behavior remains available but is not the default path for users avoiding API costs.
- Changing vector dimensions for existing databases may require a migration or database reset; preserving mixed-dimension historical embeddings is out of scope.
- Model download or cache management may require network access during setup, but normal ingestion/search should not require an external embedding API key.
