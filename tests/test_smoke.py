"""Smoke test: package imports cleanly. Replace/extend as modules land."""

import snippetory


def test_version_is_set() -> None:
    assert snippetory.__version__
