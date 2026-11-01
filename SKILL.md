---
name: snippetory
description: Look up existing code in the local repository by plain-English query before writing new helpers. Use when asked to find, reuse or locate a function, class or snippet in the current codebase.
---

# Snippetory

Snippetory keeps a local embedding index of the repository and returns the best-matching
functions and classes for a query.

## When to use

- Before writing a new helper, check whether the codebase already has one.
- When the user describes behaviour ("where do we parse config?") but not a name.

## Steps

1. Make sure the CLI is installed (`pip install -e .` in the snippetory repo, then `snippetory --help`).
2. Build or refresh the index from the project root: `snippetory index .`
3. Query: `snippetory suggest "what the code does" -n 5` (add `--json` for structured output,
   `--full` to see whole snippets).
4. Open the reported `path:start-end` ranges and reuse or adapt the code instead of duplicating it.

## Notes

- Re-run `snippetory index .` after significant edits; the index is not updated automatically.
- Exit code 1 means no snippet matched; try different keywords (identifier words work well).
- The index lives in `.snippetory/` and should not be committed.
