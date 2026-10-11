# Feature Specification: Go Corpus Extraction

**Feature Branch**: `003-go-corpus-extraction`  
**Created**: 2026-10-11  
**Status**: Draft  
**Input**: User description: "Correct extraction and create a curated multi-URL Go corpus manifest."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Style Guidance Accurately (Priority: P1)

As a developer relying on retrieved Go guidance, I need prose, inline identifiers,
code examples, headings, lists, and good-or-bad labels to retain their meaning so
that retrieved passages do not omit or distort the rules I am expected to follow.

**Why this priority**: Accurate source content is the foundation for every later
retrieval and code-generation decision. Missing or merged example content can lead
the model to apply the opposite of the intended guidance.

**Independent Test**: Ingest representative source fixtures containing nested
inline code, preformatted examples, lists, links, and heading hierarchies, then
compare the extracted sections with the expected human-readable source content.

**Acceptance Scenarios**:

1. **Given** a paragraph containing inline code between surrounding prose, **When**
   the page is extracted, **Then** the prose and inline code appear once and in the
   original reading order.
2. **Given** a preformatted Go example with nested markup, **When** the page is
   extracted, **Then** its line boundaries and code content are preserved without
   duplication.
3. **Given** guidance expressed through lists, tables, links, or labelled good and
   bad examples, **When** the page is extracted, **Then** those semantic distinctions
   remain understandable in the stored content.
4. **Given** navigation and other repeated page chrome, **When** the page is
   extracted, **Then** that boilerplate is excluded from searchable guidance.

---

### User Story 2 - Ingest the Curated Go Corpus (Priority: P2)

As a corpus maintainer, I need one reviewed manifest of Go guidance sources so that
the complete approved corpus can be ingested consistently without following
unreviewed links.

**Why this priority**: A single guide page omits important decisions, examples, and
test guidance. A reviewed source set improves coverage while maintaining a clear
trust boundary.

**Independent Test**: Start with an empty corpus, ingest the manifest, and verify
that every enabled source has exactly one active document with extracted sections
and that no unlisted link was ingested.

**Acceptance Scenarios**:

1. **Given** the default manifest, **When** a maintainer requests corpus ingestion,
   **Then** each enabled approved URL is fetched and processed exactly once.
2. **Given** a listed page containing links to other pages, **When** it is ingested,
   **Then** no linked page is ingested unless its URL also appears in the manifest.
3. **Given** an entry disabled by a maintainer, **When** the manifest is ingested,
   **Then** that source is skipped and its status is reported clearly.
4. **Given** one source fails while other sources remain available, **When** the run
   completes, **Then** successful sources remain usable and the failed source is
   reported without being represented as current successful content.

---

### User Story 3 - Review Corpus Coverage and Provenance (Priority: P3)

As a developer or maintainer, I need to see what sources and sections are active so
that I can confirm the corpus is complete, current, and trustworthy before relying
on it for retrieval.

**Why this priority**: Observable coverage makes omissions and stale sources visible
instead of silently reducing retrieval quality.

**Independent Test**: Inspect the result of a manifest ingestion and confirm it
reports the configured source identity, outcome, active section count, source
location, and content identity for every manifest entry.

**Acceptance Scenarios**:

1. **Given** a completed corpus ingestion, **When** a maintainer reviews the result,
   **Then** every manifest entry has a succeeded, failed, or skipped outcome.
2. **Given** a successfully ingested section, **When** it is returned for retrieval,
   **Then** it can be traced to its source page and section location.
3. **Given** duplicate URLs or duplicate source identifiers in the manifest, **When**
   the manifest is validated, **Then** ingestion is rejected with actionable details
   before any source is fetched.

### Edge Cases

- A page contains nested inline elements inside paragraphs, headings, list items,
  table cells, or preformatted code.
- A single content block is larger than the configured section size.
- A page has no meaningful content after boilerplate removal.
- A source redirects to a different canonical location.
- Multiple manifest entries resolve to the same canonical source.
- A page changes its heading depth or omits an expected heading.
- A code example contains characters that resemble markup or contains blank lines.
- A manifest is empty, malformed, contains an unsupported location, or contains no
  enabled sources.
- A subset of sources is temporarily unavailable or returns non-document content.
- Re-ingestion finds unchanged content, changed content, or a formerly successful
  source that now fails.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST preserve the reading order of prose and nested inline
  content during extraction.
- **FR-002**: The system MUST preserve the content and meaningful line structure of
  preformatted Go examples.
- **FR-003**: The system MUST retain meaningful headings, paragraphs, lists, tables,
  links, and example labels while excluding navigation, scripts, styling, and
  repeated page chrome.
- **FR-004**: Extracted content MUST represent each source passage once without
  unintended omission or duplication caused by nested markup.
- **FR-005**: The system MUST reject a source that yields no meaningful content and
  report an actionable failure reason.
- **FR-006**: The system MUST provide a reviewed manifest whose initial enabled
  source set covers the Google Go Style Overview, Guide, Decisions, and Best
  Practices, Effective Go, Go Code Review Comments, and Go Test Comments.
- **FR-007**: Each manifest entry MUST have a stable identifier, source location,
  human-readable title, enabled state, and corpus classification.
- **FR-008**: Manifest validation MUST reject duplicate identifiers, duplicate source
  locations, unsupported locations, and missing required values before ingestion.
- **FR-009**: Corpus ingestion MUST process only enabled sources explicitly present
  in the manifest and MUST NOT discover or ingest unlisted links.
- **FR-010**: A corpus ingestion run MUST report a succeeded, failed, or skipped
  outcome and active section count for every manifest entry.
- **FR-011**: Failure of one source MUST NOT discard successful ingestion results for
  other sources in the same run.
- **FR-012**: A failed refresh MUST NOT replace the last successfully active content
  for that source.
- **FR-013**: Re-ingesting unchanged source content MUST produce the same logical
  extracted content and MUST NOT create multiple active representations.
- **FR-014**: Every stored and retrieved section MUST remain traceable to its manifest
  source, source location, and heading path.
- **FR-015**: Extraction regression examples MUST cover the representative markup
  structures used across every source family in the initial manifest.
- **FR-016**: Maintainers MUST be able to add, disable, or update an approved source
  through the manifest without changing extraction behavior for other entries.

### Quality & Boundary Requirements

- **QB-001**: Feature behavior MUST be expressible as independently testable
  increments.
- **QB-002**: The manifest contract, source provenance, ingestion outcome, and
  agent-facing retrieval metadata MUST have explicit validation coverage.
- **QB-003**: Extraction, manifest validation, per-source ingestion, run reporting,
  storage, and retrieval MUST remain separate responsibilities with explicit
  boundaries.
- **QB-004**: Detailed markup handling and per-source outcome aggregation are expected
  design-pressure areas; their behavior MUST be decomposed so no function or method
  requires cyclomatic complexity of 4 or greater.
- **QB-005**: Existing single-URL ingestion and search consumers MUST remain usable
  unless a separately versioned contract explicitly replaces them.

### Key Entities

- **Corpus Manifest**: The reviewed definition of a named corpus and its ordered set
  of approved source entries.
- **Corpus Source**: One approved page, identified by a stable key and carrying its
  location, title, enabled state, and classification.
- **Extracted Content Block**: An ordered unit of meaningful page content, such as a
  heading, paragraph, list item, table content, or code example.
- **Document Section**: Searchable guidance derived from ordered content blocks and
  linked to its source and heading context.
- **Corpus Ingestion Run**: The aggregate result of processing a manifest, including
  one outcome and section count per source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All representative nested-markup fixtures preserve 100% of expected
  prose, identifiers, and code content in the correct reading order, with no
  unintended duplicates.
- **SC-002**: One corpus operation processes all enabled entries in the default
  manifest and reports an outcome for 100% of entries.
- **SC-003**: A corpus ingestion test confirms that zero unlisted linked pages are
  added to the corpus.
- **SC-004**: Every active searchable section can be traced to one manifest source,
  one source location, and its section heading context.
- **SC-005**: When one source is unavailable, all other available sources complete
  successfully and the unavailable source is identified accurately.
- **SC-006**: Maintainers can add or disable an approved source and complete a
  validated corpus run without modifying application behavior elsewhere.
- **SC-007**: Human review of a representative sample from every initial source finds
  no missing code examples, inverted good-or-bad labels, or boilerplate-only
  sections.

## Assumptions

- The initial corpus is the approved Google and Go project guidance named in
  FR-006; project-specific Go conventions remain outside this feature.
- Manifest ingestion is explicit and maintainer initiated; automatic discovery,
  scheduled refresh, and unrestricted crawling are outside scope.
- Public documentation pages are accessible without authentication.
- The current extraction-to-section pipeline, active-document semantics, and search
  interfaces remain available for extension.
- Source precedence and conflict resolution during model generation belong to the
  later RAG orchestration feature, not this corpus-ingestion feature.
- Correct extraction is judged by retained meaning and reading order rather than
  visual reproduction of the source page.
