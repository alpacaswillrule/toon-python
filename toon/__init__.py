"""Public API for the Python TOON encoder."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Union

from .constants import DEFAULT_DELIMITER, DELIMITERS
from .encoders import encode_value
from .normalize import normalize_value
from .types import EncodeOptions, ResolvedEncodeOptions, resolve_options

__all__ = [
    "encode",
    "EncodeOptions",
    "ResolvedEncodeOptions",
    "DEFAULT_DELIMITER",
    "DELIMITERS",
]


def encode(value: Any, options: Union[EncodeOptions, Mapping[str, Any], None] = None) -> str:
    """Encode arbitrary Python data into the TOON serialization format."""
    normalized = normalize_value(value)
    resolved = _resolve(options)
    return encode_value(normalized, resolved)


def _resolve(options: Union[EncodeOptions, Mapping[str, Any], None]) -> ResolvedEncodeOptions:
    if options is None:
        return resolve_options(None)
    if isinstance(options, EncodeOptions):
        return resolve_options(options)
    if is_dataclass(options):
        return resolve_options(EncodeOptions(**asdict(options)))
    if isinstance(options, Mapping):
        return resolve_options(EncodeOptions(**dict(options)))
    raise TypeError("options must be an EncodeOptions instance, mapping, or None")

