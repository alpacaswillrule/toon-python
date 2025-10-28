"""Primitive encoding helpers used by the TOON encoder."""

from __future__ import annotations

import math
import re
from typing import Iterable, List, Sequence

from .constants import (
    BACKSLASH,
    COMMA,
    DEFAULT_DELIMITER,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    LIST_ITEM_MARKER,
    NULL_LITERAL,
    TRUE_LITERAL,
)
from .types import JsonPrimitive, LengthMarker


def encode_primitive(value: JsonPrimitive, delimiter: str | None = None) -> str:
    if value is None:
        return NULL_LITERAL

    if isinstance(value, bool):
        return TRUE_LITERAL if value else FALSE_LITERAL

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return NULL_LITERAL
        if value == 0.0:
            return "0"
        return _format_float_js_like(value)

    delimiter = delimiter or COMMA
    return encode_string_literal(value, delimiter)


def encode_string_literal(value: str, delimiter: str = COMMA) -> str:
    if is_safe_unquoted(value, delimiter):
        return value
    return f'{DOUBLE_QUOTE}{escape_string(value)}{DOUBLE_QUOTE}'


def escape_string(value: str) -> str:
    return (
        value.replace(BACKSLASH, BACKSLASH * 2)
        .replace(DOUBLE_QUOTE, BACKSLASH + DOUBLE_QUOTE)
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    if value == "":
        return False
    if value.strip() != value:
        return False
    if value in (TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL):
        return False
    if _is_numeric_like(value):
        return False
    if ":" in value:
        return False
    if '"' in value or "\\" in value:
        return False
    if re.search(r"[\[\]\{\}]", value):
        return False
    if re.search(r"[\n\r\t]", value):
        return False
    if delimiter and delimiter in value:
        return False
    if value.startswith(LIST_ITEM_MARKER):
        return False
    return True


NUMERIC_LIKE_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?(?:e[+-]?\d+)?$", re.IGNORECASE)
LEADING_ZERO_PATTERN = re.compile(r"^0\d+$")


def _is_numeric_like(value: str) -> bool:
    return bool(NUMERIC_LIKE_PATTERN.match(value) or LEADING_ZERO_PATTERN.match(value))


def encode_key(key: str) -> str:
    if _is_valid_unquoted_key(key):
        return key
    return f'{DOUBLE_QUOTE}{escape_string(key)}{DOUBLE_QUOTE}'


VALID_KEY_PATTERN = re.compile(r"^[A-Z_][\w.]*$", re.IGNORECASE)


def _is_valid_unquoted_key(key: str) -> bool:
    return bool(VALID_KEY_PATTERN.match(key))


def join_encoded_values(values: Sequence[JsonPrimitive], delimiter: str = COMMA) -> str:
    return delimiter.join(encode_primitive(v, delimiter) for v in values)


def format_header(
    length: int,
    *,
    key: str | None = None,
    fields: Sequence[str] | None = None,
    delimiter: str = COMMA,
    length_marker: LengthMarker = False,
) -> str:
    marker = length_marker if length_marker else ""
    header = ""
    if key:
        header += encode_key(key)

    delimiter_suffix = delimiter if delimiter != DEFAULT_DELIMITER else ""
    header += f"[{marker}{length}{delimiter_suffix}]"

    if fields:
        header += "{" + delimiter.join(encode_key(field) for field in fields) + "}"

    header += ":"
    return header


def _format_float_js_like(value: float) -> str:
    abs_value = abs(value)
    if abs_value == 0.0:
        return "0"

    exponent = int(math.floor(math.log10(abs_value)))

    if -6 <= exponent <= 20:
        formatted = f"{value:.15f}".rstrip("0").rstrip(".")
    else:
        formatted = f"{value:.15e}"
        mantissa, exp = formatted.split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        sign = exp[0]
        exp_value = exp[1:].lstrip("0") or "0"
        formatted = f"{mantissa}e{sign}{exp_value}"

    if formatted == "-0":
        return "0"
    return formatted

