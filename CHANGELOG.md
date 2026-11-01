# Changelog

## [0.1.0]

### Added
- `snippetory index` builds a local embedding index (Python definitions and sliding windows
  for other languages).
- `snippetory suggest` ranks snippets by cosine similarity, with `--json`, `--full`,
  `--min-score`, `-n` and `-p` options.
- `snippetory stats` and `snippetory clear`.
- Identifier-aware tokenizer and feature-hashing embedder (numpy only, no model download).
- Claude Code skill description in `SKILL.md`.
