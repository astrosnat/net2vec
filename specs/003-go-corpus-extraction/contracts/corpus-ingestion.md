# Contract: Corpus Ingestion Command

## Invocation

```text
python -m net2vec.cli.ingest_corpus [--manifest PATH]
```

- `--manifest` is optional and defaults to the checked-in Go style manifest.
- The manifest is fully validated before network or database work begins.
- The command processes entries in manifest order.

## Success Output

The command emits one human-readable line per source followed by a summary:

```text
[succeeded] google-go-guide: 18 sections
[skipped] disabled-source: disabled in manifest
corpus go-style: 1 succeeded, 0 failed, 1 skipped
```

The process exits with code `0` when every enabled source succeeds.

## Partial Failure Output

```text
[succeeded] google-go-guide: 18 sections
[failed] go-test-comments: URL fetch failed with status 503
corpus go-style: 1 succeeded, 1 failed, 0 skipped
```

The process exits with code `1` when at least one enabled source fails. Successfully ingested sources remain active.

## Validation Failure

```text
manifest validation error: duplicate source id 'google-go-guide'
```

The process exits with code `2`. No source is fetched and no stored content changes.

## Behavioral Guarantees

- Exactly one outcome is reported for every manifest entry.
- Disabled entries are never fetched.
- Links found within fetched pages are never added implicitly.
- Error text includes source identity and useful context but excludes credentials and response bodies.
- Existing single-URL ingestion remains a separate supported command.

