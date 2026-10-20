"""Command-line interface for snippetory."""

import argparse
import sys

from . import __version__


def main(argv=None):
    """Entry point for the snippetory CLI."""
    parser = argparse.ArgumentParser(
        prog="snippetory",
        description="A Claude Code skill for suggesting code snippets from your local codebase.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Index command
    index_parser = subparsers.add_parser(
        "index", help="Index code snippets from a directory"
    )
    index_parser.add_argument(
        "path", nargs="?", default=".", help="Path to index (default: current directory)"
    )

    # Suggest command
    suggest_parser = subparsers.add_parser(
        "suggest", help="Suggest snippets based on a query"
    )
    suggest_parser.add_argument("query", help="Search query for snippets")
    suggest_parser.add_argument(
        "-n",
        "--num-results",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )

    args = parser.parse_args(argv)

    if args.command == "index":
        print(f"Indexing snippets in {args.path}...")
        # TODO: Implement indexing logic
    elif args.command == "suggest":
        print(f"Searching for: {args.query}")
        print(f"Showing top {args.num_results} results...")
        # TODO: Implement suggestion logic
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()