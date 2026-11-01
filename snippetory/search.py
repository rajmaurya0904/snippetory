"""Query the index for the most relevant snippets."""

from dataclasses import dataclass

import numpy as np

from .chunker import Chunk
from .embed import embed


@dataclass(frozen=True)
class Hit:
    """A ranked search result."""

    chunk: Chunk
    score: float


def search(
    query: str,
    chunks: list[Chunk],
    vectors: np.ndarray,
    limit: int = 5,
    min_score: float = 0.0,
) -> list[Hit]:
    """Return up to ``limit`` chunks ranked by cosine similarity to ``query``."""
    if limit <= 0 or not chunks:
        return []
    q = embed(query, vectors.shape[1])
    if not q.any():
        return []
    scores = vectors @ q
    order = np.argsort(-scores, kind="stable")
    hits = []
    for i in order:
        if float(scores[i]) <= min_score:
            break
        hits.append(Hit(chunks[i], float(scores[i])))
        if len(hits) >= limit:
            break
    return hits
