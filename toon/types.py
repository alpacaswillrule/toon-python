"""Shared typing aliases for the TOON encoder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from .constants import DEFAULT_DELIMITER, DELIMITERS, Delimiter

JsonPrimitive = Union[str, int, float, bool, None]
JsonObject = Dict[str, "JsonValue"]
JsonArray = List["JsonValue"]
JsonValue = Union[JsonPrimitive, JsonObject, JsonArray]

Depth = int
LengthMarker = Union[str, bool]


@dataclass(frozen=True)
class EncodeOptions:
    """User-supplied encoder configuration."""

    indent: Optional[int] = None
    delimiter: Optional[Delimiter] = None
    length_marker: LengthMarker = False


@dataclass(frozen=True)
class ResolvedEncodeOptions:
    """Normalized encoder options with defaults applied."""

    indent: int
    delimiter: Delimiter
    length_marker: LengthMarker


def resolve_options(options: Optional[EncodeOptions]) -> ResolvedEncodeOptions:
    indent = 2 if options is None or options.indent is None else options.indent
    delimiter = (
        DEFAULT_DELIMITER
        if options is None or options.delimiter is None
        else options.delimiter
    )
    length_marker: LengthMarker = False if options is None else options.length_marker

    if indent < 0:
        raise ValueError("indent must be non-negative")
    if delimiter not in DELIMITERS.values():
        raise ValueError(f"Unsupported delimiter {delimiter!r}")
    if length_marker not in (False, "#"):
        raise ValueError("length_marker must be False or '#'")

    return ResolvedEncodeOptions(indent=indent, delimiter=delimiter, length_marker=length_marker)
