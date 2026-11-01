"""Tests for snippetory.chunker."""

from snippetory.chunker import chunk_file, chunk_text, iter_source_files

PY = '''import os


def alpha():
    return 1


@decorator
def beta(x):
    return x


class Gamma:
    def method(self):
        pass
'''


def test_python_chunks_by_definition():
    chunks = chunk_text("m.py", PY)
    assert [c.name for c in chunks] == ["alpha", "beta", "Gamma"]


def test_decorator_included():
    beta = chunk_text("m.py", PY)[1]
    assert beta.text.startswith("@decorator")
    assert beta.start == 8


def test_class_includes_methods():
    gamma = chunk_text("m.py", PY)[2]
    assert "def method" in gamma.text


def test_syntax_error_falls_back_to_windows():
    chunks = chunk_text("bad.py", "def (:\n  nope\n")
    assert len(chunks) == 1
    assert chunks[0].start == 1


def test_window_chunks_overlap():
    text = "\n".join(f"word{i} " * 10 for i in range(100))
    chunks = chunk_text("a.md", text)
    assert len(chunks) > 1
    assert chunks[1].start <= chunks[0].end  # overlapping windows
    assert chunks[-1].end == 100


def test_empty_text_has_no_chunks():
    assert chunk_text("a.js", "") == []


def test_iter_skips_vendored_dirs(tmp_path):
    (tmp_path / "keep.py").write_text("def f(): pass\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "skip.js").write_text("x")
    (tmp_path / "notes.bin").write_text("x")
    names = [p.name for p in iter_source_files(tmp_path)]
    assert names == ["keep.py"]


def test_chunk_file_relative_path(tmp_path):
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "m.py").write_text("def f():\n    return 1\n")
    chunks = chunk_file(sub / "m.py", tmp_path)
    assert chunks[0].path == "pkg/m.py"


def test_chunk_file_skips_binary(tmp_path):
    f = tmp_path / "b.py"
    f.write_bytes(b"\xff\xfe\x00\x80")
    assert chunk_file(f, tmp_path) == []
