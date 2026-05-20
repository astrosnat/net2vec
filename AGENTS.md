# net2vec Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-08

## Active Technologies

- Python 3.14 + FastAPI, Uvicorn, Typer, Pydantic, SQLAlchemy 2.x, Alembic, psycopg 3, pgvector-python, PyTorch, Hugging Face Transformers, BeautifulSoup4, lxml, httpx, MCP Python SDK, pytest, ruff, lizard; PostgreSQL 16+ with pgvector 0.8.x storing 768-dimensional CodeBERT vectors (001-docs-vector-ingestion)

## Project Structure

```text
src/
tests/
```

## Commands

pytest
ruff check .
lizard -C 3 src tests

## Code Style

Python 3.14: Follow standard conventions

## Constitutional Constraints

- Keep cyclomatic complexity below 4 for every function or method.
- Preserve SOLID responsibilities and explicit module boundaries.
- Separate ingestion, parsing, embedding, storage, retrieval, agent interfaces,
  and orchestration when those concerns are present.
- Validate data and integration contracts at boundaries.

## Recent Changes
- 001-docs-vector-ingestion: Added Python 3.14 + FastAPI, Uvicorn, Typer, Pydantic, SQLAlchemy 2.x, Alembic, psycopg 3, pgvector-python, PyTorch, Hugging Face Transformers, BeautifulSoup4, lxml, httpx, MCP Python SDK, pytest, ruff, lizard

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
