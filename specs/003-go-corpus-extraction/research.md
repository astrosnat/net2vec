# Research: Go Corpus Extraction

## Decision: Replace stateful capture with semantic DOM traversal

Parse each HTML document into a DOM using the project's existing BeautifulSoup4 and lxml dependencies. Select the primary content root, remove known non-content elements, then emit semantic blocks in document order.

**Rationale**: The current extractor holds one active tag and buffer, so nested `<code>` content can replace its parent paragraph or preformatted capture. A DOM preserves parent-child relationships and makes it possible to render nested inline content once while treating code blocks, lists, and tables deliberately.

**Alternatives considered**:

- Add a stack to the current `HTMLParser`: feasible, but it would recreate DOM traversal, whitespace, table, and nested-block behavior manually.
- Convert the whole page to plain text: rejected because it destroys code layout, headings, example labels, and other retrieval-relevant semantics.
- Maintain source-specific scrapers: rejected because page-specific branches would be brittle and violate the shared extraction boundary.

## Decision: Emit only outermost selected semantic blocks

Select meaningful block elements under the primary content root, but do not independently emit a selected element when it has a selected semantic ancestor. Render nested inline descendants as part of the outer block. Use dedicated rendering for preformatted code, list items, and table rows.

**Rationale**: This rule prevents `<p>text <code>x</code> text</p>` from becoming overlapping paragraph and code blocks while allowing `<pre><code>...</code></pre>` to retain line structure. It also gives tests a deterministic no-duplication invariant.

**Alternatives considered**:

- Emit every matching element: rejected because nested elements duplicate content.
- Emit only text nodes: rejected because reconstructing meaningful block boundaries and code layout becomes unreliable.

## Decision: Use a versioned checked-in JSON manifest

Store the curated source list in `src/net2vec/config/corpora/go-style.json`. Validate it against an explicit versioned contract and domain rules before initiating any network request.

**Rationale**: JSON is deterministic, supported without another runtime parser, straightforward to validate and test, and suitable for a small reviewed source list. A checked-in manifest makes changes reviewable and prevents runtime link discovery from expanding the trust boundary.

**Alternatives considered**:

- YAML: readable but adds parsing behavior and ambiguity without benefit for the small schema.
- TOML: viable, but arrays of structured source entries are less concise for this data and the repository has no existing TOML configuration loader.
- Store the manifest in PostgreSQL: rejected because source approval should remain reviewable with the code and available before database access.

## Decision: Seed seven explicit official guidance sources

The initial enabled corpus contains:

1. `https://google.github.io/styleguide/go/`
2. `https://google.github.io/styleguide/go/guide`
3. `https://google.github.io/styleguide/go/decisions`
4. `https://google.github.io/styleguide/go/best-practices`
5. `https://go.dev/doc/effective_go`
6. `https://go.dev/wiki/CodeReviewComments`
7. `https://go.dev/wiki/TestComments`

**Rationale**: The Google overview identifies Guide, Decisions, and Best Practices as the related style documents and calls Effective Go a baseline. The Go review page describes itself as a supplement to Effective Go and points to Test Comments for testing guidance. These sources collectively cover principles, canonical guidance, decisions, practical patterns, community conventions, reviews, and tests.

**Alternatives considered**:

- Ingest only Google's canonical Guide: rejected because it omits detailed decisions, best practices, community baseline, and testing guidance.
- Crawl all linked resources: rejected because it makes source approval and corpus scope nondeterministic.

**Sources**:

- Google Go Style overview: https://google.github.io/styleguide/go/
- Effective Go: https://go.dev/doc/effective_go
- Go Code Review Comments: https://go.dev/wiki/CodeReviewComments
- Go Test Comments: https://go.dev/wiki/TestComments

## Decision: Reuse single-source ingestion through a corpus orchestrator

Validate the full manifest first, then process enabled entries sequentially by invoking a provenance-aware form of the existing single-source pipeline. Create a `skipped` outcome for disabled entries and catch source-scoped ingestion failures to produce `failed` outcomes while continuing the run.

**Rationale**: The current pipeline already owns URL validation, fetching, extraction, chunking, embedding, and atomic replacement after successful processing. Composition avoids duplicating these responsibilities and naturally preserves previous active content when fetching, extraction, or embedding fails before replacement.

**Alternatives considered**:

- Parallel ingestion: deferred because seven pages do not justify additional connection, model, transaction, and deterministic-reporting complexity.
- One transaction for the whole corpus: rejected because one unavailable source would discard all successful work, contrary to the specification.
- Put iteration in the CLI: rejected because HTTP or future scheduled entry points would duplicate business rules.

## Decision: Persist optional corpus provenance on source documents

Add nullable `corpus_id`, `manifest_source_id`, and `source_classification` fields to source documents. Manifest ingestion supplies them; legacy single-URL ingestion leaves them null. Search results expose these values as optional additive metadata.

**Rationale**: Source URL alone cannot reliably express a stable manifest identity if canonical locations change. Persisted identifiers allow every retrieved section to map back to the reviewed manifest while preserving compatibility for existing content.

**Alternatives considered**:

- Infer provenance by matching URLs at query time: rejected because redirects and manifest edits make the relationship unstable.
- Add separate corpus membership tables immediately: rejected as unnecessary for one curated corpus with one membership per active document; it can be introduced later if documents need many-to-many corpus membership.

## Decision: Enforce uniqueness only for active source documents

In the provenance migration, replace the existing uniqueness constraint over `(source_url, active)` with an active-only uniqueness rule on `source_url`.

**Rationale**: The current constraint permits only one inactive row for a URL, so a later successful refresh can fail once more than one historical version exists. Corpus ingestion is explicitly repeatable and needs exactly one active version while allowing any number of inactive versions.

**Alternatives considered**:

- Delete older inactive rows: rejected because it introduces destructive retention behavior unrelated to this feature.
- Update the active row in place: rejected because it changes the existing append-and-deactivate refresh model and removes useful content history.

## Decision: Treat extraction fixtures as stable regression evidence

Check in minimal, representative HTML fixtures derived from the structures used by the Google Style and go.dev source families, paired with expected semantic blocks. Keep live-fetch verification as an optional maintainer check rather than a deterministic test dependency.

**Rationale**: Live pages can change and network access can fail. Local fixtures make omission, order, whitespace, and duplication assertions repeatable while still covering both source families.

**Alternatives considered**:

- Test only synthetic one-line snippets: rejected because they miss real nested and structural interactions.
- Require live pages in the normal suite: rejected because it makes tests nondeterministic and dependent on external availability.

