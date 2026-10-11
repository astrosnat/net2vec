# Contract: Retrieval Provenance

Search results from HTTP and MCP retain all existing fields and add these optional fields:

| Field | Type | Presence | Meaning |
|-------|------|----------|---------|
| `corpus_id` | string | Manifest-ingested documents | Stable corpus identifier |
| `manifest_source_id` | string | Manifest-ingested documents | Stable source entry identifier |
| `source_classification` | string | Manifest-ingested documents | Reviewed role of the source in the corpus |
| `resolved_url` | string | When known | Final fetched location after redirects |

## Compatibility

- Existing required fields, ranks, scores, excerpts, full text, source URL, and heading paths are unchanged.
- Optional provenance fields are omitted or null for legacy single-URL documents.
- Consumers that ignore unknown fields continue to use existing result data.

## Validation

- When `corpus_id` is present, `manifest_source_id` and `source_classification` must also be present.
- `manifest_source_id` must be stable across successful refreshes of the same manifest entry.
- `source_url` remains the reviewed manifest URL; `resolved_url` records a distinct redirect destination without changing manifest identity.

