# Contract: Vector Storage

## Storage Boundary

`document_sections.embedding` stores the vector used for pgvector similarity search.

## Required Schema

| Column | Required Shape |
|--------|----------------|
| `document_sections.embedding` | 768-dimensional vector |
| `document_sections.embedding_dimensions` | integer metadata equal to `768` for local defaults |
| `document_sections.embedding_model` | model identity used to generate the vector |

## Migration Expectations

- Fresh schema creation must produce a 768-dimensional vector column.
- SQLAlchemy model metadata must match Alembic migration metadata.
- Existing local development databases using 1536-dimensional vectors must be recreated or explicitly migrated before local embeddings are used.

## Validation Expectations

- Ingestion must not store vectors whose length differs from configured dimensions.
- Search must not compare query vectors against incompatible stored vectors.
- Tests must verify model/migration vector dimensions remain aligned.
