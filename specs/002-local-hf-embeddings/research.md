# Research: Local Embedding Provider

## Decision: Add an explicit embedding provider setting

Use `NET2VEC_EMBEDDING_PROVIDER` with supported values `local` and `openai`. Default to `local`, because the feature's primary goal is to remove the external API key requirement for local development.

**Rationale**: A provider setting makes behavior predictable across CLI, HTTP, and MCP entry points and prevents accidental fallback to a paid external service.

**Alternatives considered**:

- Infer provider from `OPENAI_API_KEY`: rejected because an existing key in the environment could silently choose the paid path.
- Infer provider from model name: rejected because model names are not a stable provider contract.

## Decision: Use CodeBERT-compatible local defaults

Use `NET2VEC_EMBEDDING_MODEL=microsoft/codebert-base` and `NET2VEC_EMBEDDING_DIMENSIONS=768` for local mode.

**Rationale**: The original feature plan and README already describe CodeBERT-sized embeddings as the intended local direction. This also aligns storage with a smaller local vector dimension than the current OpenAI default.

**Alternatives considered**:

- Keep `text-embedding-3-small` and 1536 dimensions as defaults: rejected because it keeps the API-cost path as the default.
- Support arbitrary mixed dimensions in one database: rejected as out of scope and unnecessary for the local-first feature.

## Decision: Load the local model through Transformers and PyTorch

Use Hugging Face Transformers `AutoTokenizer` and `AutoModel` for local model loading. Run the model in evaluation mode and PyTorch inference mode.

**Rationale**: Hugging Face documents `from_pretrained()` as the standard path for loading pretrained model weights and configuration. PyTorch documents `inference_mode` as appropriate for workloads that do not interact with autograd, while also noting that `model.eval()` must still be called for inference behavior.

**Alternatives considered**:

- Use the Transformers `pipeline` abstraction: rejected because raw vectors and deterministic pooling are the feature boundary.
- Use sentence-transformers: rejected for this feature because the current plan explicitly targets Hugging Face/PyTorch and CodeBERT.

**Sources**:

- Hugging Face Transformers loading models: https://huggingface.co/docs/transformers/main/models
- Hugging Face Transformers Auto Classes: https://huggingface.co/transformers/v4.7.0/model_doc/auto.html
- PyTorch `inference_mode`: https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html

## Decision: Use masked mean pooling over last hidden states

Convert token-level model output to a single vector by applying the attention mask to the last hidden state and averaging non-padding tokens. Normalize the resulting vector before returning it.

**Rationale**: `AutoModel` returns model outputs suitable for downstream processing, while CodeBERT is not a dedicated sentence embedding API. Masked mean pooling gives one deterministic fixed-size vector per input and avoids relying on task-specific classifier heads.

**Alternatives considered**:

- Use only the first token vector: simpler but often less representative of full documentation chunks.
- Use an unmasked average: rejected because padding tokens would affect vector values.
- Add a projection layer: rejected because it would require training or unexplained weights.

## Decision: Centralize provider construction in an embedding factory

Add a small factory that accepts settings and returns `EmbeddingService` configured with the correct client, model, and dimension. API, CLI, and MCP entry points will call that factory.

**Rationale**: Current code repeats `OpenAIEmbeddingClient` construction in multiple entry points. Centralizing selection keeps provider behavior consistent and avoids provider-specific branching in unrelated modules.

**Alternatives considered**:

- Add provider branching directly in each entry point: rejected because it duplicates logic and risks divergent behavior.
- Move all settings into `EmbeddingService`: rejected because provider selection is configuration/adaptation, while the service should orchestrate embedding calls and validation.

## Decision: Make vector storage 768-dimensional for the local-first schema

Update SQLAlchemy model and initial Alembic migration to use `Vector(768)`. Existing local development databases with the old 1536-dimensional vector column should be recreated or migrated before using local mode.

**Rationale**: pgvector vector columns have a fixed dimension in this schema. The feature scope favors a local-first database contract over mixed historical compatibility.

**Alternatives considered**:

- Keep `Vector(1536)` and pad local vectors: rejected because padded vectors distort similarity and hide configuration errors.
- Store variable dimensions as arrays: rejected because it weakens pgvector search behavior and departs from the current schema.
- Add parallel vector columns: rejected as unnecessary for local-first single-provider operation.

**Sources**:

- pgvector documentation: https://github.com/pgvector/pgvector
