# net2vec

`net2vec` is a small tool developed to ingest texts from the web, vector embed them, and connect them to AI agents. `net2vec` is designed to make automated software development easier and more token-efficient.

## Local Development

```powershell
python -m pip install -e ".[dev]"
pytest
ruff check .
lizard -C 3 src tests
```

Copy `.env.example` to `.env` or export the variables in your shell before
running ingestion. The first feature quickstart is in
`specs/001-docs-vector-ingestion/quickstart.md`.
