"""Tests for snippetory.config."""

from snippetory.config import (
    CHUNK_SIZE,
    DATABASE_PATH,
    EMBEDDING_DIMENSIONS,
    OVERLAP,
)


def test_embedding_dimensions() -> None:
    assert EMBEDDING_DIMENSIONS == 384


def test_chunk_size() -> None:
    assert CHUNK_SIZE == 256


def test_overlap() -> None:
    assert OVERLAP == 32


def test_database_path() -> None:
    assert DATABASE_PATH == ".snippetory/vectors"