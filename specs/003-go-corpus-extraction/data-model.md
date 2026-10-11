# Data Model: Go Corpus Extraction

## Corpus Manifest

Represents a versioned, reviewed collection of documentation sources.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| schema_version | integer | Yes | Must equal a supported manifest schema version; initial value is `1` |
| corpus_id | string | Yes | Stable lowercase identifier; initial value is `go-style` |
| title | string | Yes | Non-empty human-readable corpus name |
| sources | ordered list of Corpus Source | Yes | Must contain at least one entry and at least one enabled entry |

### Validation Rules

- The complete manifest is validated before any source is fetched.
- `corpus_id` is stable across ordinary source additions or removals.
- Source order is retained for deterministic execution and reporting.
- Duplicate source identifiers or normalized source URLs invalidate the manifest.

## Corpus Source

Represents one explicitly approved documentation page.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| id | string | Yes | Stable lowercase identifier, unique within the manifest |
| url | absolute URL | Yes | HTTPS URL, unique after exact-URL normalization |
| title | string | Yes | Non-empty reviewed display name |
| classification | string | Yes | One of `overview`, `canonical`, `normative`, `best-practice`, `baseline`, `review`, or `testing` |
| enabled | boolean | Yes | Controls whether the entry is fetched; disabled entries are still reported |

### Initial Entries

| ID | Classification | URL |
|----|----------------|-----|
| google-go-overview | overview | `https://google.github.io/styleguide/go/` |
| google-go-guide | canonical | `https://google.github.io/styleguide/go/guide` |
| google-go-decisions | normative | `https://google.github.io/styleguide/go/decisions` |
| google-go-best-practices | best-practice | `https://google.github.io/styleguide/go/best-practices` |
| effective-go | baseline | `https://go.dev/doc/effective_go` |
| go-code-review-comments | review | `https://go.dev/wiki/CodeReviewComments` |
| go-test-comments | testing | `https://go.dev/wiki/TestComments` |

## Extracted Content Block

Represents one ordered semantic unit emitted from a documentation page.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| kind | enum | Yes | `heading`, `text`, `code`, `list-item`, or `table-row` |
| level | integer | Yes | Heading depth for headings; `0` for other block kinds |
| text | string | Yes | Non-empty content with kind-appropriate whitespace normalization |
| ordinal | integer | Yes | Zero-based source order after boilerplate removal |

### Validation Rules

- Text and nested inline content retain reading order.
- Inline code is represented within its containing prose exactly once.
- Preformatted code retains meaningful newlines and indentation.
- List items and table rows retain readable item/cell boundaries.
- Empty blocks and blocks contained entirely in excluded page chrome are omitted.

## Source Document Provenance

Extends an ingested source document with optional manifest identity.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| corpus_id | string or null | No | Set for manifest ingestion; null for legacy single-URL ingestion |
| manifest_source_id | string or null | No | Must identify an entry in the named manifest when set |
| source_classification | string or null | No | Copied from the manifest entry when set |
| source_url | URL | Yes | Existing submitted source identity |
| resolved_url | URL | No | Final location after redirects, retained when different from source URL |
| content_hash | string | No | Identity of successfully retrieved content |
| active | boolean | Yes | At most one active successful document per source URL |

### Compatibility Rules

- Existing documents remain valid with all new provenance fields null.
- A successful manifest refresh creates or updates active content with the same stable provenance.
- A failed refresh does not deactivate the preceding successful document.
- Active-only uniqueness permits exactly one active document for a source URL and any number of inactive historical documents.
- Search response additions are optional so existing single-URL results remain valid.

## Corpus Source Outcome

Represents the result of one manifest entry in a corpus run.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| source_id | string | Yes | Matches the manifest entry |
| source_url | URL | Yes | Submitted manifest URL |
| status | enum | Yes | `succeeded`, `failed`, or `skipped` |
| sections_indexed | integer | Yes | Non-negative; zero for skipped or failed entries |
| document_id | identifier or null | No | Present only when successful content is active |
| content_hash | string or null | No | Present after successful ingestion |
| message | string or null | No | Actionable failure or skip detail without secrets |

### State Transitions

```text
enabled entry  -> processing -> succeeded
enabled entry  -> processing -> failed
disabled entry -------------> skipped
```

Each enabled entry reaches exactly one terminal state independently of other entries.

## Corpus Ingestion Run

Represents a deterministic attempt to process one validated manifest.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| corpus_id | string | Yes | Copied from the manifest |
| started_at | timestamp | Yes | Run start time |
| completed_at | timestamp | Yes | Set after all entries have terminal outcomes |
| outcomes | ordered list of Corpus Source Outcome | Yes | Exactly one outcome per manifest entry, in manifest order |
| succeeded | integer | Yes | Count derived from outcomes |
| failed | integer | Yes | Count derived from outcomes |
| skipped | integer | Yes | Count derived from outcomes |

### Validation Rules

- Invalid manifests do not create a run or fetch sources.
- Outcome counts sum to the number of manifest entries.
- Partial failure is represented by the outcomes and a non-success process result while preserving successful entries.

