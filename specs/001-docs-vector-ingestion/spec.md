# Feature Specification: Documentation Vector Ingestion

**Feature Branch**: `001-docs-vector-ingestion`  
**Created**: 2026-04-24  
**Status**: Draft  
**Input**: User description: "I want to build a system that takes webpages like the go style guide and vector embeds them so an agent like codex or claude can just crawl through that. The system should take this shape at a high level: 1. A URL ingestion script. 2. A Postgres database with pgvector. 3. A chunking strategy based on headings. 4. An embedding step. 5. A search API. 6. An MCP server exposing search_docs. 7. A Codex/Claude config pointing to that MCP server."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest a Documentation Page (Priority: P1)

A developer provides the URL for a web documentation page and the system adds
that page to the searchable documentation corpus, preserving enough source and
heading context for later citation.

**Why this priority**: Search has no value until source documentation can be
captured reliably and traced back to its original page.

**Independent Test**: Provide a URL for a public style guide page, run ingestion,
and verify the corpus records the page, its title, source URL, heading
structure, and searchable text sections.

**Acceptance Scenarios**:

1. **Given** a reachable documentation URL, **When** the developer ingests it, **Then** the system stores the page as a searchable document with its source URL and page title.
2. **Given** a page with multiple headings, **When** ingestion completes, **Then** the resulting sections retain the heading path needed to understand each excerpt.
3. **Given** the same URL has already been ingested, **When** the developer ingests it again, **Then** the corpus is refreshed without creating duplicate active records for the same page.

---

### User Story 2 - Search Ingested Documentation (Priority: P2)

A developer or agent searches the documentation corpus using a natural-language
question and receives relevant excerpts with enough context to decide whether
the result is useful.

**Why this priority**: The main outcome is enabling agents and humans to find
relevant guidance without manually browsing long documentation pages.

**Independent Test**: Ask a style-guide question whose answer appears in an
ingested page and verify the returned results include relevant excerpts, source
URLs, headings, and relevance ordering.

**Acceptance Scenarios**:

1. **Given** documentation has been ingested, **When** a user searches for a concept from that documentation, **Then** the system returns the most relevant excerpts first.
2. **Given** a returned excerpt, **When** the user reviews the result, **Then** the result includes the original URL and heading context for source verification.
3. **Given** no relevant documentation exists, **When** a user searches the corpus, **Then** the system returns an empty result with a clear no-match outcome.

---

### User Story 3 - Let Agents Query Documentation (Priority: P3)

An agent such as Codex or Claude is configured to use the documentation search
tool and can call `search_docs` to retrieve relevant source-grounded excerpts
during an assisted development workflow.

**Why this priority**: Agent access is the feature's end-to-end value, but it
depends on ingestion and search already working.

**Independent Test**: Configure an agent client against the local documentation
search tool, ask it a question about an ingested guide, and verify it calls
`search_docs` and uses returned source-grounded excerpts.

**Acceptance Scenarios**:

1. **Given** the search tool is running and configured, **When** an agent receives a documentation question, **Then** the agent can call `search_docs` with the user's query.
2. **Given** `search_docs` returns results, **When** the agent presents an answer, **Then** the answer can cite or reference the returned source URLs and headings.
3. **Given** the search tool is unavailable, **When** the agent attempts to use it, **Then** the failure is clear enough for the developer to diagnose the missing service or configuration.

---

### Edge Cases

- A URL is unreachable, times out, redirects repeatedly, or returns unsupported content.
- A page contains little or no heading structure.
- A page contains navigation, boilerplate, generated markup, or duplicate text.
- A source page changes after it was previously ingested.
- Search queries are vague, very long, empty, or unrelated to the corpus.
- Multiple documentation pages contain similar guidance with conflicting wording.
- The agent configuration points to a stopped, moved, or unauthorized search tool.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a developer to ingest a documentation webpage by URL.
- **FR-002**: System MUST capture each ingested page's source URL, title when available, retrieval status, and ingestion timestamp.
- **FR-003**: System MUST divide documentation content into searchable sections that preserve heading context when headings are present.
- **FR-004**: System MUST remove or minimize non-content page elements that would reduce search quality, such as navigation and repeated boilerplate.
- **FR-005**: System MUST refresh an already-ingested URL without creating duplicate active search results for the same source content.
- **FR-006**: System MUST make ingested documentation searchable by natural-language query.
- **FR-007**: System MUST return search results with excerpt text, source URL, heading context, and a relevance rank or score.
- **FR-008**: System MUST expose an agent-callable tool named `search_docs` for querying ingested documentation.
- **FR-009**: System MUST provide configuration instructions or generated configuration for agent clients to connect to `search_docs`.
- **FR-010**: System MUST report clear, actionable errors for failed ingestion, empty corpora, unavailable search services, and invalid search requests.
- **FR-011**: System MUST allow search results to be limited by result count to keep agent responses concise.
- **FR-012**: System MUST preserve enough source context for a user to verify retrieved excerpts against the original webpage.

### Quality & Boundary Requirements

- **QB-001**: Feature behavior MUST be expressible as independently testable
  increments.
- **QB-002**: Requirements MUST identify affected data schemas, integration
  contracts, or agent-facing behavior.
- **QB-003**: Requirements MUST flag any expected design pressure that could
  exceed cyclomatic complexity 3 per function or method.
- **QB-004**: Planning MUST explicitly account for branching-heavy areas such as
  ingestion failures, content extraction, refresh behavior, and search result
  formatting so each unit remains below the project complexity limit.

### Key Entities *(include if feature involves data)*

- **Source Document**: A webpage submitted for ingestion, including its URL,
  title, retrieval metadata, and active status.
- **Document Section**: A searchable excerpt derived from a source document,
  including text, heading path, order within the document, and source reference.
- **Search Query**: A user or agent request for relevant documentation, including
  query text and optional result limit.
- **Search Result**: A ranked section returned for a query, including excerpt,
  source URL, heading context, and relevance information.
- **Agent Tool Configuration**: Connection details that let an agent client call
  the documentation search tool.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can ingest a single public documentation page and make it searchable in under 2 minutes during a local workflow.
- **SC-002**: For a known question answered by ingested documentation, the correct source section appears in the top 3 search results at least 90% of the time across a representative test set.
- **SC-003**: 95% of searches over a small local documentation corpus return results or a clear no-match outcome within 2 seconds.
- **SC-004**: Every returned result includes a source URL and heading context in 100% of successful searches.
- **SC-005**: An agent configured for the tool can successfully call `search_docs` and receive usable results in a documented end-to-end validation.

## Assumptions

- The initial users are developers running the system for local or team
  documentation search.
- The first supported sources are public documentation webpages with text content.
- Search access is intended for trusted local or internal agent clients, not a
  public anonymous service.
- The initial corpus size is small to moderate documentation collections rather
  than a full web-scale crawler.
- The exact storage engine, embedding provider, and service framework will be
  selected during planning while preserving the user-requested end-to-end shape.
