"""Tests for snippetory.tokenizer."""

from snippetory.tokenizer import split_identifier, tokenize


def test_snake_case_split():
    assert tokenize("parse_config_file") == ["parse", "config", "file"]


def test_camel_case_keeps_full_name():
    assert tokenize("parseConfig") == ["parse", "config", "parseconfig"]


def test_split_camel_case():
    assert split_identifier("parseConfigFile") == ["parse", "config", "file"]


def test_split_acronym():
    assert split_identifier("HTTPServer") == ["http", "server"]


def test_stopwords_removed():
    assert "the" not in tokenize("the quick fox")
    assert "quick" in tokenize("the quick fox")


def test_keep_stopwords():
    assert "the" in tokenize("the fox", keep_stopwords=True)


def test_empty_text():
    assert tokenize("") == []


def test_numbers_kept():
    assert "404" in tokenize("status 404")
