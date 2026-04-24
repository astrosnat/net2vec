# Data Model: Documentation Vector Ingestion

## SourceDocument

Represents one exact submitted documentation URL.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | Yes | Stable internal identifier |
| source_url | URL string | Yes | Canonical unique URL for active content |
| title | string | No | Extracted page title when available |
| retrieval_status | enum | Yes | `pending`, `succeeded`, `failed` |
| http_status | integer | No | HTTP status from latest fetch |
| content_hash | string | No | Hash of extracted main content |
| active | boolean | Yes | Exactly one active record per source URL |
| ingested_at | timestamp | Yes | First successful ingestion timestamp |
| refreshed_at | timestamp | Yes | Latest refresh timestamp |
| error_message | string | No | Sanitized latest failure reason |

### Validation Rules

- `source_url` MUST be absolute HTTP or HTTPS.
- The system MUST NOT crawl URLs linked from `source_url`.
- Refreshing the same `source_url` MUST replace previous active chunks.
- Failed refreshes MUST NOT remove the last successful active content unless no
  active content exists yet.

### Relationships

- Has many `DocumentSection` records.

### State Transitions

```text
pending -> succeeded
pending -> failed
succeeded -> pending -> succeeded
succeeded -> pending -> failed
failed -> pending -> succeeded
failed -> pending -> failed
```

## DocumentSection

Represents one heading-aware searchable chunk.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | Yes | Stable internal identifier |
| document_id | UUID | Yes | Parent `SourceDocument` |
| chunk_index | integer | Yes | Source order within active document |
| heading_path | string array | Yes | Heading ancestry, empty only if no headings exist |
| heading_text | string | No | Nearest heading |
| excerpt | string | Yes | Concise search display text |
| full_chunk_text | string | Yes | Complete stored chunk returned by search |
| token_count | integer | Yes | Estimated chunk size |
| content_hash | string | Yes | Chunk-level duplicate detection |
| embedding_model | string | Yes | Model used to create the embedding |
| embedding_dimensions | integer | Yes | Vector size |
| embedding | vector | Yes | pgvector embedding |
| active | boolean | Yes | Mirrors active source document version |
| created_at | timestamp | Yes | Chunk creation timestamp |

### Validation Rules

- `chunk_index` MUST be unique within an active `document_id`.
- `full_chunk_text` MUST be non-empty after trimming.
- `excerpt` MUST be derived from `full_chunk_text`.
- `embedding_dimensions` MUST match the configured embedding model.
- Search results MUST include `excerpt`, `full_chunk_text`, `source_url`,
  `heading_path`, and relevance information.

### Relationships

- Belongs to one `SourceDocument`.
- Appears in zero or more `SearchResult` responses.

## SearchQuery

Represents a user or Codex request to search the corpus.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| query | string | Yes | Natural-language query |
| limit | integer | No | Defaults to 5 |

### Validation Rules

- `query` MUST contain non-whitespace text.
- `limit` MUST be between 1 and 20.
- Empty corpus searches return a clear no-match response, not an error.

## SearchResult

Represents one ranked chunk returned to a user or Codex.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| section_id | UUID | Yes | Matched `DocumentSection` |
| document_id | UUID | Yes | Parent `SourceDocument` |
| source_url | URL string | Yes | Original source page |
| title | string | No | Source document title |
| heading_path | string array | Yes | Heading ancestry |
| excerpt | string | Yes | Concise result text |
| full_chunk_text | string | Yes | Complete stored chunk |
| rank | integer | Yes | 1-based result rank |
| score | number | Yes | Similarity or distance-derived score |

### Validation Rules

- Results MUST be ordered by relevance.
- Results MUST only include active document sections.
- Every result MUST include source URL and heading context.

## AgentToolConfiguration

Represents Codex connection details for the local MCP server.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| server_name | string | Yes | Suggested name: `net2vec` |
| transport | enum | Yes | `streamable_http` for initial version |
| url | URL string | Yes | Local/internal MCP endpoint |
| tool_name | string | Yes | Must be `search_docs` |

### Validation Rules

- Initial configuration MUST target Codex only.
- Generated documentation MUST state trusted local/internal use only.
- Configuration MUST fail clearly when the MCP server is unavailable.
