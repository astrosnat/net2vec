# Data Model: Local Embedding Provider

## Embedding Mode Configuration

Represents the runtime choice of embedding source and vector shape.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| provider | string | Yes | Must be `local` or `openai`; defaults to `local` |
| model | string | Yes | Defaults to local CodeBERT model for local mode |
| dimensions | integer | Yes | Must equal the vector length returned by the selected provider |
| openai_api_key | string | Conditional | Required only when provider is `openai` |

### Validation Rules

- Unsupported provider values fail before ingestion or search starts.
- `openai_api_key` is required only for `openai`.
- Local provider does not require an external embedding API key.
- Provider, model, and dimensions are shared by CLI, HTTP, and MCP entry points.

## Document Section Vector

Represents a stored documentation chunk embedding used for search.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| embedding_model | string | Yes | Model identity used to create the vector |
| embedding_dimensions | integer | Yes | Must match configured dimensions |
| embedding | vector | Yes | Must fit storage schema dimension |

### Validation Rules

- Generated vectors are validated before storage.
- Stored local vectors use 768 dimensions.
- Search query vectors must match active document-section vector dimensions.

## Search Query Vector

Represents the runtime vector generated from a search query.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| query_text | string | Yes | Non-empty search text from HTTP or MCP contracts |
| embedding_model | string | Yes | Same configured model as active document-section vectors |
| embedding_dimensions | integer | Yes | Same configured dimension as active document-section vectors |
| embedding | vector | Yes | Must pass embedding service dimension validation |

### Validation Rules

- Empty query validation remains owned by existing API/domain contracts.
- Embedding generation uses the configured provider through the shared service.
- Dimension mismatch fails before repository search.

## Vector Storage Schema

Represents the database contract for persisted embeddings.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| document_sections.embedding | vector | Yes | Local-first schema stores 768-dimensional vectors |
| document_sections.embedding_dimensions | integer | Yes | Metadata records the configured vector size |
| document_sections.embedding_model | string | Yes | Metadata records the configured model identity |

### Compatibility Notes

- Fresh databases use 768-dimensional vector storage.
- Existing local development databases created with 1536 dimensions require migration or recreation.
- Mixed dimensions in one active corpus are out of scope for this feature.
