# Contract: Embedding Configuration

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NET2VEC_EMBEDDING_PROVIDER` | No | `local` | Selects the embedding provider. Supported values: `local`, `openai`. |
| `NET2VEC_EMBEDDING_MODEL` | No | `microsoft/codebert-base` | Model identifier used by the selected provider. |
| `NET2VEC_EMBEDDING_DIMENSIONS` | No | `768` | Expected vector length for generated embeddings. |
| `OPENAI_API_KEY` | Only for `openai` | Empty | External API credential used only when provider is `openai`. |

## Required Behavior

- CLI ingestion, HTTP search, and MCP search must resolve configuration through the same provider-selection path.
- Unsupported provider values must raise a clear configuration error before fetching, embedding, storing, or searching.
- Local provider must not read or require `OPENAI_API_KEY`.
- OpenAI provider must fail clearly when `OPENAI_API_KEY` is missing.
- Generated vectors must be validated against `NET2VEC_EMBEDDING_DIMENSIONS`.

## Error Shape Expectations

- CLI: exits with code `2` and prints a clear embedding configuration error to stderr.
- HTTP API: returns status `400` with `error` set to `invalid_embedding_configuration`.
- MCP tool: raises `MCPValidationError` without returning partial search results.
