"""On-disk vector store: a numpy matrix plus JSON metadata."""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .chunker import Chunk
from .config import DATABASE_PATH, EMBEDDING_DIMENSIONS

VECTORS_FILE = "vectors.npy"
META_FILE = "meta.json"


class StoreError(Exception):
    """Raised when the index is missing or unreadable."""


def store_dir(base: Path | str, database_path: str = DATABASE_PATH) -> Path:
    """Directory holding the index for ``base``."""
    return Path(base) / database_path


def save(directory: Path, chunks: list[Chunk], vectors: np.ndarray, root: str) -> None:
    """Write the index to ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    np.save(directory / VECTORS_FILE, vectors.astype(np.float32))
    meta = {"root": root, "dims": int(vectors.shape[1]), "chunks": [asdict(c) for c in chunks]}
    (directory / META_FILE).write_text(json.dumps(meta, indent=1), encoding="utf-8")


def load(directory: Path) -> tuple[list[Chunk], np.ndarray, str]:
    """Load ``(chunks, vectors, root)`` from ``directory``."""
    vec_path = directory / VECTORS_FILE
    meta_path = directory / META_FILE
    if not vec_path.exists() or not meta_path.exists():
        raise StoreError(f"no index found in {directory}; run 'snippetory index' first")
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        vectors = np.load(vec_path)
        chunks = [Chunk(**c) for c in meta["chunks"]]
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise StoreError(f"index in {directory} is corrupt: {exc}") from exc
    if vectors.shape != (len(chunks), meta.get("dims", EMBEDDING_DIMENSIONS)):
        raise StoreError(f"index in {directory} is inconsistent; re-run 'snippetory index'")
    return chunks, vectors, meta.get("root", "")


def clear(directory: Path) -> bool:
    """Delete the index files; return True if anything was removed."""
    removed = False
    for name in (VECTORS_FILE, META_FILE):
        f = directory / name
        if f.exists():
            f.unlink()
            removed = True
    try:
        directory.rmdir()
    except OSError:
        pass
    return removed
