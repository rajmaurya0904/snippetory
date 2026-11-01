"""Command-line interface for snippetory."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__, store
from .indexer import build_index
from .search import search

PREVIEW_LINES = 6


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snippetory",
        description="Suggest relevant code snippets from your local codebase.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_index = sub.add_parser("index", help="Index code snippets from a directory")
    p_index.add_argument(
        "path", nargs="?", default=".", help="Path to index (default: current directory)"
    )

    p_index.add_argument(
        "-x",
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Skip files whose relative path matches GLOB (repeatable, e.g. 'tests/*')",
    )

    p_suggest = sub.add_parser("suggest", help="Suggest snippets based on a query")
    p_suggest.add_argument("query", help="Search query for snippets")
    p_suggest.add_argument(
        "-n", "--num-results", type=int, default=5, help="Number of results (default: 5)"
    )
    p_suggest.add_argument(
        "-p", "--path", default=".", help="Indexed directory to search (default: .)"
    )
    p_suggest.add_argument(
        "--min-score", type=float, default=0.05, help="Minimum similarity score (default: 0.05)"
    )
    p_suggest.add_argument("--json", action="store_true", help="Print results as JSON")
    p_suggest.add_argument(
        "--full", action="store_true", help="Print whole snippets instead of a short preview"
    )

    p_stats = sub.add_parser("stats", help="Show information about the current index")
    p_stats.add_argument("-p", "--path", default=".", help="Indexed directory (default: .)")

    p_clear = sub.add_parser("clear", help="Delete the index")
    p_clear.add_argument("-p", "--path", default=".", help="Indexed directory (default: .)")
    return parser


def _cmd_index(args: argparse.Namespace) -> int:
    try:
        result = build_index(args.path, tuple(args.exclude))
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Indexed {result.chunks} snippets from {result.files} files")
    print(f"Index written to {result.location}")
    return 0


def _preview(text: str, full: bool) -> str:
    lines = text.splitlines()
    shown = lines if full else lines[:PREVIEW_LINES]
    out = "\n".join(f"    {line}" for line in shown)
    if len(shown) < len(lines):
        out += f"\n    ... ({len(lines) - len(shown)} more lines)"
    return out


def _cmd_suggest(args: argparse.Namespace) -> int:
    try:
        chunks, vectors, _ = store.load(store.store_dir(args.path))
    except store.StoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    hits = search(args.query, chunks, vectors, args.num_results, args.min_score)
    if args.json:
        payload = [
            {
                "path": h.chunk.path,
                "start": h.chunk.start,
                "end": h.chunk.end,
                "name": h.chunk.name,
                "score": round(h.score, 4),
                "text": h.chunk.text,
            }
            for h in hits
        ]
        print(json.dumps(payload, indent=2))
        return 0 if hits else 1
    if not hits:
        print(f"No snippets matched '{args.query}'")
        return 1
    for rank, hit in enumerate(hits, 1):
        c = hit.chunk
        print(f"{rank}. {c.path}:{c.start}-{c.end}  {c.name}  (score {hit.score:.2f})")
        print(_preview(c.text, args.full))
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    try:
        chunks, vectors, root = store.load(store.store_dir(args.path))
    except store.StoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Root:       {root}")
    print(f"Files:      {len({c.path for c in chunks})}")
    print(f"Snippets:   {len(chunks)}")
    print(f"Dimensions: {vectors.shape[1]}")
    return 0


def _cmd_clear(args: argparse.Namespace) -> int:
    location = store.store_dir(Path(args.path))
    if store.clear(location):
        print(f"Removed index at {location}")
    else:
        print("No index to remove")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the snippetory CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "index": _cmd_index,
        "suggest": _cmd_suggest,
        "stats": _cmd_stats,
        "clear": _cmd_clear,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


def run() -> None:
    """Console-script wrapper that turns the return code into an exit status."""
    sys.exit(main())


if __name__ == "__main__":
    run()
