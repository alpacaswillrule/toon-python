"""Utility for building indented multi-line TOON output."""

from __future__ import annotations

from typing import List

from .types import Depth


class LineWriter:
    """Collects lines with consistent indentation."""

    __slots__ = ("_lines", "_indent_string")

    def __init__(self, indent_size: int) -> None:
        self._lines: List[str] = []
        self._indent_string = " " * indent_size

    def push(self, depth: Depth, content: str) -> None:
        indent = self._indent_string * depth
        self._lines.append(f"{indent}{content}")

    def to_string(self) -> str:
        return "\n".join(self._lines)

