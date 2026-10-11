# Quickstart: Go Corpus Extraction

## 1. Install and Configure net2vec

```powershell
python -m pip install -e ".[dev]"
$env:DATABASE_URL = "postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec"
$env:NET2VEC_EMBEDDING_PROVIDER = "local"
$env:NET2VEC_EMBEDDING_MODEL = "microsoft/codebert-base"
$env:NET2VEC_EMBEDDING_DIMENSIONS = "768"
```

Expected result: application, database, and local embedding dependencies are available.

## 2. Prepare the Database

```powershell
python -m net2vec.persistence.migrations upgrade
```

Expected result: source documents support optional corpus provenance while existing single-URL records remain valid.

## 3. Inspect the Curated Manifest

Review `src/net2vec/config/corpora/go-style.json`.

Expected enabled sources:

- Google Go Style Overview
- Google Go Style Guide
- Google Go Style Decisions
- Google Go Style Best Practices
- Effective Go
- Go Code Review Comments
- Go Test Comments

The manifest is an allowlist. Links on those pages are not crawled.

## 4. Ingest the Complete Corpus

```powershell
python -m net2vec.cli.ingest_corpus
```

Expected result: one outcome is printed for each of the seven sources, followed by succeeded, failed, and skipped totals. A failure for one page does not discard successful pages or replace that page's previous successful content.

## 5. Verify Provenance Through Search

```powershell
python -m uvicorn net2vec.api.app:app --host 127.0.0.1 --port 8000
```

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/search" `
  -ContentType "application/json" `
  -Body '{"query":"How should Go tests report got and want values?","limit":3}'
```

Expected result: matches include their existing content and ranking fields plus the stable `go-style` corpus identity, manifest source identity, classification, and source location.

## 6. Run Validation

```powershell
python -m pytest -ra
python -m ruff check .
python -m lizard -C 3 src tests
```

Expected result: extraction golden tests, manifest validation, partial-failure integration tests, provenance contracts, existing tests, linting, and complexity checks all pass.

## 7. Optional Live Source Review

Run corpus ingestion against a disposable local database and manually inspect representative sections from every source family.

Expected result: prose and inline identifiers remain in reading order, code examples retain meaningful layout, good/bad labels are not inverted, and no navigation-only section is stored.
