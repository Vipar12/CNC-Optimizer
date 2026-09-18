"""Lexer for a lightweight G-code dialect."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class Token:
    """A single lexical token from the input G-code stream."""

    kind: str
    value: str
    line_number: int


class GCodeLexer:
    """Splits a G-code line into logical tokens while preserving the raw text."""

    TOKEN_RE = re.compile(r"(?P<word>[A-Za-z])(?P<number>[-+]?\d*\.?\d+)")

    @classmethod
    def tokenize_line(cls, line: str, line_number: int) -> list[Token]:
        text = line.split(";", 1)[0].strip()
        if not text:
            return []

        tokens: list[Token] = []
        for match in cls.TOKEN_RE.finditer(text):
            letter = match.group("word").upper()
            value = match.group("number")
            tokens.append(Token(kind=letter, value=value, line_number=line_number))
        return tokens
