"""Unit tests for the CLI interface."""

import sys
from unittest.mock import patch

import pytest

from snippetory.cli import main


def test_index_default_path(capsys):
    """Test index command with default path."""
    with patch.object(sys, 'argv', ['snippetory', 'index']):
        main()
    captured = capsys.readouterr()
    assert "Indexing snippets in ." in captured.out


def test_index_explicit_path(capsys):
    """Test index command with explicit path."""
    with patch.object(sys, 'argv', ['snippetory', 'index', '/some/path']):
        main()
    captured = capsys.readouterr()
    assert "Indexing snippets in /some/path" in captured.out


def test_suggest_default_num_results(capsys):
    """Test suggest command with default number of results."""
    with patch.object(sys, 'argv', ['snippetory', 'suggest', 'foo']):
        main()
    captured = capsys.readouterr()
    assert "Searching for: foo" in captured.out
    assert "Showing top 5 results" in captured.out


def test_suggest_custom_num_results(capsys):
    """Test suggest command with custom number of results."""
    with patch.object(sys, 'argv', ['snippetory', 'suggest', 'foo', '-n', '10']):
        main()
    captured = capsys.readouterr()
    assert "Searching for: foo" in captured.out
    assert "Showing top 10 results" in captured.out


def test_version(capsys):
    """Test version flag."""
    with patch.object(sys, 'argv', ['snippetory', '--version']):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    # Version output goes to stdout
    assert 'snippetory' in captured.out


def test_no_command(capsys):
    """Test behavior when no command is provided."""
    with patch.object(sys, 'argv', ['snippetory']):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    # Help message is printed to stdout
    assert 'usage:' in captured.out.lower()
    assert 'index' in captured.out
    assert 'suggest' in captured.out