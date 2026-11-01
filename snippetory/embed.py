"""Lightweight deterministic text embeddings via feature hashing (no model download)."""

import hashlib

import numpy as np

from .config import EMBEDDING_DIMENSIONS
from .tokenizer import tokenize


def _bucket(feature: str, dims: int) -> tuple[int, float]:
    """Hash a feature to a (bucket index, sign) pair."""
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "little")
    sign = 1.0 if value & 1 else -1.0
    return (value >> 1) % dims, sign


def features(text: str) -> list[str]:
    """Unigram and bigram features for ``text``."""
    tokens = tokenize(text)
    feats = list(tokens)
    feats.extend(f"{a}_{b}" for a, b in zip(tokens, tokens[1:], strict=False))
    return feats


def embed(text: str, dims: int = EMBEDDING_DIMENSIONS) -> np.ndarray:
    """Embed ``text`` as an L2-normalised float32 vector of length ``dims``.

    Term frequency is dampened with ``1 + log(tf)`` so repeated words do not dominate.
    """
    counts: dict[str, int] = {}
    for feat in features(text):
        counts[feat] = counts.get(feat, 0) + 1
    vec = np.zeros(dims, dtype=np.float32)
    for feat, count in counts.items():
        idx, sign = _bucket(feat, dims)
        vec[idx] += sign * (1.0 + float(np.log(count)))
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def embed_many(texts: list[str], dims: int = EMBEDDING_DIMENSIONS) -> np.ndarray:
    """Embed several texts into an ``(n, dims)`` matrix."""
    if not texts:
        return np.zeros((0, dims), dtype=np.float32)
    return np.vstack([embed(t, dims) for t in texts])
