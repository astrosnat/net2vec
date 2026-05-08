# Research: Documentation Vector Ingestion

## Decision: Python 3.12 Single-Service Project

**Rationale**: Python has mature libraries for HTTP fetching, HTML parsing,
local CodeBERT embeddings, PostgreSQL access, API serving, CLI tooling, and MCP
server implementation. A single package keeps the first version small while
preserving clear adapter boundaries.

**Alternatives considered**:
- TypeScript: strong MCP ecosystem, but less aligned with common Python data and
  text extraction tooling for this project.
- Go: good for simple services, but slower path for local model embedding and
  MCP server ergonomics in this repo's initial state.

## Decision: PostgreSQL 16+ with pgvector 0.8.x

**Rationale**: The user requested PostgreSQL with pgvector. Current pgvector
documentation describes vector similarity search inside PostgreSQL, including
exact and approximate nearest neighbor search, cosine distance, and PostgreSQL
13+ support. Keeping vectors with document metadata simplifies refresh
transactions and one-active-version constraints.

**Alternatives considered**:
- Dedicated vector database: unnecessary for the initial small to moderate
  corpus and would add operational surface.
- SQLite vector extension: simpler local setup, but conflicts with the requested
  PostgreSQL/pgvector shape.

**Source**: https://github.com/pgvector/pgvector

## Decision: CodeBERT `microsoft/codebert-base` for Embeddings

**Rationale**: The updated specification explicitly requires CodeBERT. Microsoft
publishes `microsoft/codebert-base` as pretrained CodeBERT weights for
programming languages and natural language, and the official CodeBERT repository
documents loading it through Hugging Face Transformers. The model configuration
uses 768-dimensional hidden states, so stored vectors, validation, migration
planning, and query embeddings must consistently use dimension 768. The plan
stores the model name and dimension with each chunk so the corpus can be
re-embedded if a future feature changes the model.

**Alternatives considered**:
- OpenAI `text-embedding-3-small`: already fits generic text search and existing
  implementation direction, but it conflicts with the explicit CodeBERT
  requirement.
- GraphCodeBERT: code-aware and closely related, but it is a different model
  family than the requested CodeBERT and would expand scope.
- Generic sentence-transformer models: may perform better on natural-language
  document retrieval, but they do not satisfy the explicit CodeBERT constraint.

**Sources**:
- https://huggingface.co/microsoft/codebert-base
- https://huggingface.co/microsoft/codebert-base/blob/main/config.json
- https://github.com/microsoft/CodeBERT

## Decision: Heading-Aware DOM Chunking

**Rationale**: The spec requires chunks based on headings. Fetching raw HTML,
removing boilerplate, and traversing heading elements keeps a heading path with
each chunk. Chunks should target 400-900 tokens with overlap only inside long
heading sections, preserving source order and heading ancestry.

**Alternatives considered**:
- Fixed-size token windows only: easier, but loses the hierarchy needed for
  citation and source verification.
- Markdown conversion first: useful later, but risks losing source DOM structure
  before headings and boilerplate are handled.

## Decision: FastAPI HTTP Search API

**Rationale**: FastAPI gives typed request/response models, generated OpenAPI,
and straightforward local serving. HTTP search also provides a stable boundary
for tests and future clients independent of MCP.

**Alternatives considered**:
- CLI-only search: easier, but does not satisfy the requested search API.
- MCP-only search: would couple all search validation to an agent transport.

## Decision: MCP Python SDK with `search_docs` Tool

**Rationale**: The official MCP SDK list identifies Python as a Tier 1 SDK, and
the Python SDK supports building servers exposing tools over local or remote
transports. The MCP layer should be a thin adapter over the same search service
used by the HTTP API.

**Alternatives considered**:
- Custom MCP protocol handling: unnecessary complexity and higher compatibility
  risk.
- TypeScript MCP server: viable, but would split the implementation across
  languages without current benefit.

**Source**: https://modelcontextprotocol.io/docs/sdk

## Decision: Codex Configuration Targets `~/.codex/config.toml`

**Rationale**: Official OpenAI developer documentation states Codex can connect
to MCP servers through the CLI/IDE shared configuration and shows direct
configuration in `~/.codex/config.toml` under `[mcp_servers.<name>]` with a URL.
The feature will generate or document a Codex-only config snippet for the local
MCP server.

**Alternatives considered**:
- Claude Desktop config: explicitly out of scope after clarification.
- Generic MCP config only: less directly useful for the clarified Codex-only
  first version.

**Source**: https://developers.openai.com/learn/docs-mcp

## Decision: Trusted Local/Internal Access Only

**Rationale**: The clarified spec excludes public access. The initial search API
and MCP server should bind to localhost by default, document trusted/internal
use, and avoid claiming production authentication. This keeps the first version
aligned with the spec while leaving API-key or OAuth requirements for a future
public deployment feature.

**Alternatives considered**:
- API keys for all access: safer for shared deployment, but extra scope for the
  initial local/internal workflow.
- Public authenticated service: directly contradicts the clarified initial
  access model.

## Decision: Complexity Gates Use lizard plus Review

**Rationale**: The constitution requires cyclomatic complexity below 4.
`lizard -C 3` directly maps to "fail at complexity 4 or higher", while review
ensures SOLID and separation-of-concerns compliance where metrics are
insufficient.

**Alternatives considered**:
- Manual review only: easy to miss violations.
- Broad refactoring framework: unnecessary before code exists.
