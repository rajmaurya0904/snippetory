"""Tests for snippetory.store and snippetory.search."""

import numpy as np
import pytest

from snippetory import store
from snippetory.chunker import Chunk
from snippetory.embed import embed_many
from snippetory.search import search

TEXTS = [
    "def read_json_file(path): open json file and parse",
    "def draw_button(canvas): render html button widget",
    "def connect_database(url): open sql database connection",
]


@pytest.fixture
def index():
    chunks = [Chunk("a.py", i + 1, i + 1, f"f{i}", t) for i, t in enumerate(TEXTS)]
    return chunks, embed_many(TEXTS)


def test_roundtrip(tmp_path, index):
    chunks, vecs = index
    store.save(tmp_path / "db", chunks, vecs, "/proj")
    loaded, lvecs, root = store.load(tmp_path / "db")
    assert loaded == chunks
    assert np.allclose(lvecs, vecs)
    assert root == "/proj"


def test_load_missing(tmp_path):
    with pytest.raises(store.StoreError, match="no index"):
        store.load(tmp_path / "nope")


def test_load_corrupt(tmp_path, index):
    chunks, vecs = index
    store.save(tmp_path, chunks, vecs, "r")
    (tmp_path / store.META_FILE).write_text("{not json")
    with pytest.raises(store.StoreError, match="corrupt"):
        store.load(tmp_path)


def test_load_inconsistent(tmp_path, index):
    chunks, vecs = index
    store.save(tmp_path, chunks[:2], vecs, "r")
    with pytest.raises(store.StoreError, match="inconsistent"):
        store.load(tmp_path)


def test_clear(tmp_path, index):
    chunks, vecs = index
    store.save(tmp_path / "db", chunks, vecs, "r")
    assert store.clear(tmp_path / "db") is True
    assert store.clear(tmp_path / "db") is False


def test_search_ranks_relevant_first(index):
    chunks, vecs = index
    hits = search("parse a json file", chunks, vecs)
    assert hits[0].chunk.name == "f0"


def test_search_limit(index):
    chunks, vecs = index
    assert len(search("database connection json button", chunks, vecs, limit=2)) == 2


def test_search_empty_query(index):
    chunks, vecs = index
    assert search("the of", chunks, vecs) == []


def test_search_no_chunks():
    assert search("x", [], np.zeros((0, 384), dtype=np.float32)) == []


def test_search_min_score(index):
    chunks, vecs = index
    assert search("json", chunks, vecs, min_score=0.99) == []
