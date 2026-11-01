"""Split source text into lowercase search tokens."""

import re

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*|\d+")
_CAMEL_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")

STOPWORDS = frozenset(
    {
        "the", "a", "an", "of", "to", "in", "is", "it", "and", "or", "for", "on",
        "self", "return", "if", "else", "def", "class", "import", "from", "none",
        "true", "false", "this", "that", "with", "as", "by", "be", "not",
    }
)  # fmt: skip


def split_identifier(word: str) -> list[str]:
    """Split ``camelCase`` / ``snake_case`` / ``HTTPServer`` words into lowercase parts."""
    parts = _CAMEL_RE.findall(word)
    return [p.lower() for p in parts if p]


def tokenize(text: str, keep_stopwords: bool = False) -> list[str]:
    """Return lowercase tokens for ``text``.

    Identifiers are split on case changes and underscores, and the full lowercase identifier is
    kept alongside its parts so exact names still score highly.
    """
    tokens: list[str] = []
    for word in _WORD_RE.findall(text.replace("_", " ")):
        parts = split_identifier(word)
        tokens.extend(parts)
        if len(parts) > 1:
            tokens.append(word.lower())
    if keep_stopwords:
        return tokens
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]
