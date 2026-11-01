# Snippetory

**Find the code you already wrote. Snippetory indexes your local codebase into small
embedding vectors and suggests the most relevant existing functions and classes for a
plain-English query -- no model download, no network, no API key.**

Every project has the helper you wrote six months ago and can no longer find. `grep` needs the
exact name; Snippetory matches on meaning-ish overlap (identifier parts, bigrams) so
"split camelCase identifiers into words" finds `split_identifier`. It also ships as a
Claude Code skill (see [SKILL.md](SKILL.md)) so the agent can look up your own code before
writing new code.

## Example

```console
$ snippetory index .
Indexed 90 snippets from 19 files
Index written to C:\Users\Raj\Desktop\rajmaurya-repos\snippetory\.snippetory\vectors

$ snippetory suggest "split camelCase identifiers into words" -n 2
1. snippetory/tokenizer.py:17-20  split_identifier  (score 0.41)
    def split_identifier(word: str) -> list[str]:
        """Split ``camelCase`` / ``snake_case`` / ``HTTPServer`` words into lowercase parts."""
        parts = _CAMEL_RE.findall(word)
        return [p.lower() for p in parts if p]
2. tests/test_tokenizer.py:14-15  test_split_camel_case  (score 0.41)
    def test_split_camel_case():
        assert split_identifier("parseConfigFile") == ["parse", "config", "file"]

$ snippetory stats
Root:       C:\Users\Raj\Desktop\rajmaurya-repos\snippetory
Files:      19
Snippets:   90
Dimensions: 384
```

## Install

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
snippetory --help
```

Requires Python 3.11+ and numpy.

## Usage

```bash
snippetory index [PATH]            # build the index (default: current directory)
snippetory suggest "QUERY"         # top matching snippets
snippetory stats                   # what is in the index
snippetory clear                   # delete the index
```

### Options

| Command   | Option                | Meaning                                              |
|-----------|-----------------------|------------------------------------------------------|
| `index`   | `-x, --exclude GLOB`  | skip files whose relative path matches (repeatable)  |
| `suggest` | `-n, --num-results N` | number of results (default 5)                        |
| `suggest` | `-p, --path DIR`      | directory whose index to search (default `.`)        |
| `suggest` | `--min-score X`       | drop results scoring below X (default 0.05)          |
| `suggest` | `--json`              | machine-readable output with full snippet text       |
| `suggest` | `--full`              | print whole snippets instead of a 6-line preview     |
| `stats`, `clear` | `-p, --path DIR` | directory whose index to use                         |

Exit codes: `0` success, `1` no results (or no command), `2` error such as a missing index.

## How it works

- Walks the tree, skipping `.git`, `.venv`, `node_modules`, build output and files over 1 MB.
- Python files are split on top-level functions and classes (via `ast`, decorators included);
  other languages use sliding windows of 256 tokens with 32 tokens of overlap.
- Text is tokenized with identifier splitting (`parseConfig` -> `parse`, `config`,
  `parseconfig`) and stopword removal.
- Unigrams and bigrams are feature-hashed (signed hashing, log-dampened term frequency)
  into a 384-dimension L2-normalised vector.
- Vectors live in `.snippetory/vectors/vectors.npy` with metadata in `meta.json`; search is a
  single matrix-vector product (cosine similarity).

## Limitations

- Lexical, not semantic: it matches shared words and identifier parts, not synonyms.
- No incremental updates; `snippetory index` rebuilds the whole index.
- Tests are indexed too and can outrank implementations for generic queries; use
  `snippetory index . -x 'tests/*'` to leave them out.
- Only Python gets definition-aware chunking.

## Development

```bash
pip install -e ".[dev]"
python -m pytest -q
ruff check .
```

## License

MIT -- see [LICENSE](LICENSE).
