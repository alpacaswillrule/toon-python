"""Utilities for normalizing arbitrary Python values into TOON-friendly JSON structures."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any, Iterable

from .types import JsonArray, JsonObject, JsonPrimitive, JsonValue


def normalize_value(value: Any) -> JsonValue:
    """Convert arbitrary Python values into JSON-compatible structures."""
    if value is None:
        return None

    if isinstance(value, (str, bool)):
        return value

    if isinstance(value, (int, float)):
        if isinstance(value, bool):
            # bool is a subclass of int, but we already covered actual bool at top
            return bool(value)
        if isinstance(value, float):
            if value == 0.0:
                return 0
            if not math.isfinite(value):
                return None
        return value

    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, set):
        return [normalize_value(item) for item in value]

    if isinstance(value, Mapping):
        return {
            str(key): normalize_value(val)
            for key, val in value.items()
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [normalize_value(item) for item in value]

    # Fallback for objects with __dict__
    if hasattr(value, "__dict__"):
        return {
            str(key): normalize_value(val)
            for key, val in vars(value).items()
        }

    return None


def is_json_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def is_json_array(value: Any) -> bool:
    return isinstance(value, list)


def is_json_object(value: Any) -> bool:
    return isinstance(value, dict)


def is_array_of_primitives(value: JsonArray) -> bool:
    return all(is_json_primitive(item) for item in value)


def is_array_of_arrays(value: JsonArray) -> bool:
    return all(is_json_array(item) for item in value)


def is_array_of_objects(value: JsonArray) -> bool:
    return all(is_json_object(item) for item in value)

