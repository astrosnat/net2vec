# Extraction Fixtures

This directory contains minimal HTML fixtures used to verify documentation
extraction without depending on live network content.

Fixtures may reproduce the structural patterns of the approved Google Go Style
and go.dev source families, including nested inline code, preformatted examples,
lists, tables, headings, links, and good-or-bad labels. Keep copied source text to
the smallest excerpt needed to demonstrate the extraction behavior under test.

For every fixture:

- record the public source URL and retrieval date in an HTML comment;
- retain only markup relevant to the regression scenario;
- remove scripts, analytics, unrelated navigation, and personal data;
- pair source-family fixtures with expected semantic blocks in
  `expected_blocks.json`;
- update the expected output intentionally when upstream structure changes.

The normal test suite must use these local fixtures. Live-source ingestion is an
optional maintainer check documented in the feature quickstart.
