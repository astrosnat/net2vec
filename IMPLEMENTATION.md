# Recommended Implementation Order

1. Correct extraction and create a curated multi-URL Go corpus manifest.
2. Build a real retrieval evaluation set and implement tokenizer-aware chunking.
3. Introduce hybrid retrieval, relevance thresholds, reranking, and stable section anchors.
4. Add a `review_go_code` or `write_go_code` orchestration tool that always grounds output in retrieved rules.
5. Add `gofmt`, compilation, test, and vet validation with a repair pass.
6. Fix the database uniqueness constraint, vector index, session lifecycle, and ingestion failure handling.
7. Run an A/B generation benchmark proving that RAG reduces measured Go style violations.
