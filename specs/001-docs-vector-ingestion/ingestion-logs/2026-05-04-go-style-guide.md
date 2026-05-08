# Ingestion Log: Google Go Style Guide

Date: 2026-05-04

## Source Selection

- Primary source: https://google.github.io/styleguide/go/guide
- Source title: Go Style Guide
- Rationale: The Go wiki style page points readers to CodeReviewComments,
  TestComments, CSSStyleGuide, and Google's Go Style Guide. The Google guide is
  the page explicitly titled "Go Style Guide" and marks itself as normative and
  canonical for Google Go style.

## Run Context

- Pipeline: `net2vec.ingestion.pipeline.IngestionPipeline`
- Fetcher: `net2vec.ingestion.fetcher.HttpFetcher`
- Repository: `InMemoryDocumentRepository`
- Embedding model: `deterministic-local-log`
- Embedding dimensions: 8
- Note: The production CLI requires PostgreSQL and an OpenAI embedding key.
  Those environment variables were not configured in this shell, so this log
  records a live fetch and in-memory ingestion run using deterministic local
  embeddings for traceability.

## Result

- Source URL: https://google.github.io/styleguide/go/guide
- Retrieved page title: `styleguide | Style guides for Google-originated open-source projects`
- Retrieval status: `succeeded`
- HTTP status: 200
- Document ID: `c18890d6-3276-468e-a144-360a3fbaef37`
- Document content hash:
  `8108cfa43e013a016b92d7c9b56d0989b363da74c4884ab43fee3670967cb256`
- Active chunks: 18
- Total chunk words: 2730

## Chunk Samples

First chunk:

- Heading path: `Go Style Guide`
- Token count: 37
- Excerpt: `https://google.github.io/styleguide/go/guide Overview | Guide | Decisions | Best practices Note: This is part of a series of documents that outline Go Style at Google. This document is normative and canonical . See the overview for more information.`

Last chunk:

- Heading path: `Go Style Guide > Core guidelines > Local consistency`
- Token count: 231
- Excerpt: `Where the style guide has nothing to say about a particular point of style, authors are free to choose the style that they prefer, unless the code in close proximity (usually within the same file or package, but sometimes within a team or project directory) has taken a consisten...`

## Structured Logs

```text
INFO httpx HTTP Request: GET https://google.github.io/styleguide/go/guide "HTTP/1.1 200 OK"
INFO net2vec.ingestion.pipeline ingested documentation page
```
