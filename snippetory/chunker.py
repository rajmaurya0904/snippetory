"""Split source files into snippet chunks."""

import ast
from dataclasses import dataclass
from pathlib import Path

from .config import CHUNK_SIZE, OVERLAP

SOURCE_EXTENSIONS = frozenset(
    {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".h", ".cpp", ".cs",
     ".rb", ".php", ".sh", ".md"}
)  # fmt: skip
SKIP_DIRS = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", ".snippetory", "build", "dist",
     ".pytest_cache", ".ruff_cache", ".mypy_cache"}
)  # fmt: skip
MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class Chunk:
    """A contiguous region of a source file."""

    path: str
    start: int  # 1-based, inclusive
    end: int  # 1-based, inclusive
    name: str
    text: str


def _python_chunks(path: str, text: str) -> list[Chunk]:
    """One chunk per top-level function/class (methods are included in their class)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines()
    chunks = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        start = node.lineno
        if node.decorator_list:
            start = min(d.lineno for d in node.decorator_list)
        end = node.end_lineno or node.lineno
        chunks.append(Chunk(path, start, end, node.name, "\n".join(lines[start - 1 : end])))
    return chunks


def _window_chunks(
    path: str, text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP
) -> list[Chunk]:
    """Fallback: sliding windows of roughly ``size`` whitespace tokens with ``overlap``."""
    lines = text.splitlines()
    chunks: list[Chunk] = []
    start = 0
    while start < len(lines):
        count = 0
        end = start
        while end < len(lines) and (count < size or end == start):
            count += len(lines[end].split())
            end += 1
        body = "\n".join(lines[start:end])
        if body.strip():
            chunks.append(Chunk(path, start + 1, end, Path(path).name, body))
        if end >= len(lines):
            break
        # step back so that about ``overlap`` tokens are shared with the next window
        back = 0
        shared = 0
        while end - back - 1 > start and shared < overlap:
            back += 1
            shared += len(lines[end - back].split())
        start = max(end - back, start + 1)
    return chunks


def chunk_text(path: str, text: str) -> list[Chunk]:
    """Chunk ``text``; Python files split on definitions, others use sliding windows."""
    if path.endswith(".py"):
        chunks = _python_chunks(path, text)
        if chunks:
            return chunks
    return _window_chunks(path, text)


def iter_source_files(root: Path):
    """Yield indexable files under ``root`` in sorted order, skipping vendored dirs."""
    root = Path(root)
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
            continue
        rel_parts = path.relative_to(root).parts[:-1]
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        yield path


def chunk_file(path: Path, root: Path) -> list[Chunk]:
    """Read ``path`` and chunk it, labelling chunks with a path relative to ``root``."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    rel = path.name if Path(root).is_file() else path.relative_to(root).as_posix()
    return chunk_text(rel, text)
