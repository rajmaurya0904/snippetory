"""Build an index for a directory tree."""

from dataclasses import dataclass
from pathlib import Path

from . import store
from .chunker import chunk_file, iter_source_files
from .embed import embed_many


@dataclass(frozen=True)
class IndexResult:
    """Summary of an indexing run."""

    files: int
    chunks: int
    location: Path


def build_index(root: Path | str, exclude: tuple[str, ...] = ()) -> IndexResult:
    """Chunk and embed every source file under ``root`` and save the index inside it."""
    root = Path(root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"path does not exist: {root}")
    base = root.parent if root.is_file() else root
    chunks = []
    files = 0
    for path in iter_source_files(root, exclude):
        found = chunk_file(path, root)
        if found:
            files += 1
            chunks.extend(found)
    vectors = embed_many([f"{c.name} {c.text}" for c in chunks])
    location = store.store_dir(base)
    store.save(location, chunks, vectors, str(root))
    return IndexResult(files=files, chunks=len(chunks), location=location)
