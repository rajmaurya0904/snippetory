"""Tests for snippetory.embed."""

import numpy as np

from snippetory.embed import embed, embed_many


def test_embed_shape_and_norm():
    vec = embed("read a json file")
    assert vec.shape == (384,)
    assert abs(float(np.linalg.norm(vec)) - 1.0) < 1e-5


def test_embed_deterministic():
    assert np.array_equal(embed("load config"), embed("load config"))


def test_embed_empty_is_zero():
    assert not embed("").any()


def test_similar_text_scores_higher():
    q = embed("parse json file")
    close = embed("def parse_json_file(path): load json")
    far = embed("render html template to the screen")
    assert float(q @ close) > float(q @ far)


def test_embed_many_shape():
    assert embed_many(["a b", "c d", "e f"]).shape == (3, 384)


def test_embed_many_empty():
    assert embed_many([]).shape == (0, 384)
