"""Tests for the command-line interface."""

import json

import pytest

from snippetory.cli import main

SAMPLE = '''def read_json_file(path):
    """Open a JSON file and parse it."""
    import json
    with open(path) as fh:
        return json.load(fh)


def draw_button(canvas):
    """Render an html button widget."""
    return canvas.button()
'''


@pytest.fixture
def project(tmp_path):
    (tmp_path / "util.py").write_text(SAMPLE)
    return tmp_path


def _index(project, capsys):
    assert main(["index", str(project)]) == 0
    return capsys.readouterr().out


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "snippetory" in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    assert main([]) == 1
    out = capsys.readouterr().out
    assert "usage:" in out.lower()
    assert "suggest" in out


def test_index_reports_counts(project, capsys):
    out = _index(project, capsys)
    assert "Indexed 2 snippets from 1 files" in out
    assert (project / ".snippetory" / "vectors" / "meta.json").exists()


def test_index_missing_path(tmp_path, capsys):
    assert main(["index", str(tmp_path / "nope")]) == 2
    assert "does not exist" in capsys.readouterr().err


def test_suggest_finds_relevant(project, capsys):
    _index(project, capsys)
    assert main(["suggest", "parse json file", "-p", str(project)]) == 0
    assert capsys.readouterr().out.startswith("1. util.py:1-5  read_json_file")


def test_suggest_without_index(tmp_path, capsys):
    assert main(["suggest", "x", "-p", str(tmp_path)]) == 2
    assert "no index" in capsys.readouterr().err


def test_suggest_no_match(project, capsys):
    _index(project, capsys)
    assert main(["suggest", "zebra quantum", "-p", str(project)]) == 1
    assert "No snippets matched" in capsys.readouterr().out


def test_suggest_json(project, capsys):
    _index(project, capsys)
    assert main(["suggest", "html button", "-p", str(project), "--json", "-n", "1"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["name"] == "draw_button"
    assert data[0]["start"] == 8


def test_suggest_json_no_match_is_empty_list(project, capsys):
    _index(project, capsys)
    assert main(["suggest", "zebra", "-p", str(project), "--json"]) == 1
    assert json.loads(capsys.readouterr().out) == []


def test_suggest_long_snippet_truncated_unless_full(tmp_path, capsys):
    body = "\n".join(f"    x{i} = {i}" for i in range(20))
    (tmp_path / "big.py").write_text(f"def long_function():\n{body}\n")
    _index(tmp_path, capsys)
    main(["suggest", "long function", "-p", str(tmp_path)])
    assert "more lines" in capsys.readouterr().out
    main(["suggest", "long function", "-p", str(tmp_path), "--full"])
    assert "x19 = 19" in capsys.readouterr().out


def test_stats(project, capsys):
    _index(project, capsys)
    assert main(["stats", "-p", str(project)]) == 0
    out = capsys.readouterr().out
    assert "Snippets:   2" in out
    assert "Dimensions: 384" in out


def test_stats_without_index(tmp_path, capsys):
    assert main(["stats", "-p", str(tmp_path)]) == 2


def test_clear(project, capsys):
    _index(project, capsys)
    assert main(["clear", "-p", str(project)]) == 0
    assert "Removed" in capsys.readouterr().out
    assert main(["clear", "-p", str(project)]) == 0
    assert "No index" in capsys.readouterr().out


def test_reindex_is_stable(project, capsys):
    first = _index(project, capsys).splitlines()[0]
    second = _index(project, capsys).splitlines()[0]
    assert first == second


def test_index_single_file(project, capsys):
    assert main(["index", str(project / "util.py")]) == 0
    assert "Indexed 2 snippets from 1 files" in capsys.readouterr().out


def test_index_exclude(project, capsys):
    (project / "tests").mkdir()
    (project / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n")
    assert main(["index", str(project), "-x", "tests/*"]) == 0
    assert "Indexed 2 snippets from 1 files" in capsys.readouterr().out
    assert main(["index", str(project)]) == 0
    assert "Indexed 3 snippets from 2 files" in capsys.readouterr().out
