"""Core encoding logic for converting normalized values into TOON."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from .constants import LIST_ITEM_MARKER, LIST_ITEM_PREFIX
from .normalize import (
    is_array_of_arrays,
    is_array_of_objects,
    is_array_of_primitives,
    is_json_array,
    is_json_object,
    is_json_primitive,
)
from .primitives import (
    encode_key,
    encode_primitive,
    format_header,
    join_encoded_values,
)
from .types import Depth, JsonArray, JsonObject, JsonPrimitive, JsonValue, ResolvedEncodeOptions
from .writer import LineWriter


def encode_value(value: JsonValue, options: ResolvedEncodeOptions) -> str:
    if is_json_primitive(value):
        return encode_primitive(value, options.delimiter)

    writer = LineWriter(options.indent)

    if is_json_array(value):
        encode_array(None, value, writer, 0, options)
    elif is_json_object(value):
        encode_object(value, writer, 0, options)

    return writer.to_string()


def encode_object(value: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    for key, item in value.items():
        encode_key_value_pair(key, item, writer, depth, options)


def encode_key_value_pair(key: str, value: JsonValue, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    encoded_key = encode_key(key)

    if is_json_primitive(value):
        writer.push(depth, f"{encoded_key}: {encode_primitive(value, options.delimiter)}")
    elif is_json_array(value):
        encode_array(key, value, writer, depth, options)
    elif is_json_object(value):
        if not value:
            writer.push(depth, f"{encoded_key}:")
        else:
            writer.push(depth, f"{encoded_key}:")
            encode_object(value, writer, depth + 1, options)


def encode_array(
    key: str | None,
    value: JsonArray,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    if not value:
        header = format_header(len(value), key=key, delimiter=options.delimiter, length_marker=options.length_marker)
        writer.push(depth, header)
        return

    if is_array_of_primitives(value):
        encode_inline_primitive_array(key, value, writer, depth, options)
        return

    if is_array_of_arrays(value):
        if all(is_array_of_primitives(arr) for arr in value):
            encode_array_of_arrays_as_list_items(key, value, writer, depth, options)
            return

    if is_array_of_objects(value):
        header = detect_tabular_header(value)
        if header:
            encode_array_of_objects_as_tabular(key, value, header, writer, depth, options)
            return

    encode_mixed_array_as_list_items(key, value, writer, depth, options)


def encode_inline_primitive_array(
    prefix: str | None,
    values: Sequence[JsonPrimitive],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    formatted = format_inline_array(values, options.delimiter, prefix, options.length_marker)
    writer.push(depth, formatted)


def encode_array_of_arrays_as_list_items(
    prefix: str | None,
    values: Sequence[JsonArray],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    header = format_header(len(values), key=prefix, delimiter=options.delimiter, length_marker=options.length_marker)
    writer.push(depth, header)

    for arr in values:
        if is_array_of_primitives(arr):
            inline = format_inline_array(arr, options.delimiter, None, options.length_marker)
            writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")


def format_inline_array(
    values: Sequence[JsonPrimitive],
    delimiter: str,
    prefix: str | None,
    length_marker: str | bool,
) -> str:
    header = format_header(len(values), key=prefix, delimiter=delimiter, length_marker=length_marker)
    if not values:
        return header
    joined_value = join_encoded_values(values, delimiter)
    return f"{header} {joined_value}"


def encode_array_of_objects_as_tabular(
    prefix: str | None,
    rows: Sequence[JsonObject],
    header: Sequence[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    header_str = format_header(
        len(rows),
        key=prefix,
        fields=header,
        delimiter=options.delimiter,
        length_marker=options.length_marker,
    )
    writer.push(depth, header_str)
    write_tabular_rows(rows, header, writer, depth + 1, options)


def detect_tabular_header(rows: Sequence[JsonObject]) -> List[str] | None:
    if not rows:
        return None
    first_row = rows[0]
    if not first_row:
        return None
    header = list(first_row.keys())
    if is_tabular_array(rows, header):
        return header
    return None


def is_tabular_array(rows: Sequence[JsonObject], header: Sequence[str]) -> bool:
    header_set = set(header)
    for row in rows:
        if set(row.keys()) != header_set:
            return False
        for key in header:
            if not is_json_primitive(row.get(key)):
                return False
    return True


def write_tabular_rows(
    rows: Sequence[JsonObject],
    header: Sequence[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    for row in rows:
        values = [row[key] for key in header]
        joined_value = join_encoded_values(values, options.delimiter)
        writer.push(depth, joined_value)


def encode_mixed_array_as_list_items(
    prefix: str | None,
    items: Sequence[JsonValue],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    header = format_header(len(items), key=prefix, delimiter=options.delimiter, length_marker=options.length_marker)
    writer.push(depth, header)

    for item in items:
        if is_json_primitive(item):
            writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{encode_primitive(item, options.delimiter)}")
        elif is_json_array(item):
            if is_array_of_primitives(item):
                inline = format_inline_array(item, options.delimiter, None, options.length_marker)
                writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
            else:
                writer.push(depth + 1, LIST_ITEM_MARKER)
                encode_array(None, item, writer, depth + 2, options)
        elif is_json_object(item):
            encode_object_as_list_item(item, writer, depth + 1, options)


def encode_object_as_list_item(obj: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    items = list(obj.items())
    if not items:
        writer.push(depth, LIST_ITEM_MARKER)
        return

    first_key, first_value = items[0]
    encoded_first_key = encode_key(first_key)

    if is_json_primitive(first_value):
        writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_first_key}: {encode_primitive(first_value, options.delimiter)}")
    elif is_json_array(first_value):
        if is_array_of_primitives(first_value):
            formatted = format_inline_array(first_value, options.delimiter, first_key, options.length_marker)
            writer.push(depth, f"{LIST_ITEM_PREFIX}{formatted}")
        elif is_array_of_objects(first_value):
            header = detect_tabular_header(first_value)
            if header:
                header_str = format_header(
                    len(first_value),
                    key=first_key,
                    fields=header,
                    delimiter=options.delimiter,
                    length_marker=options.length_marker,
                )
                writer.push(depth, f"{LIST_ITEM_PREFIX}{header_str}")
                write_tabular_rows(first_value, header, writer, depth + 1, options)
            else:
                writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_first_key}[{len(first_value)}]:")
                for item in first_value:
                    encode_object_as_list_item(item, writer, depth + 1, options)
        else:
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_first_key}[{len(first_value)}]:")
            for item in first_value:
                if is_json_primitive(item):
                    writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{encode_primitive(item, options.delimiter)}")
                elif is_json_array(item) and is_array_of_primitives(item):
                    inline = format_inline_array(item, options.delimiter, None, options.length_marker)
                    writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
                elif is_json_object(item):
                    encode_object_as_list_item(item, writer, depth + 1, options)
    elif is_json_object(first_value):
        if not first_value:
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_first_key}:")
        else:
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_first_key}:")
            encode_object(first_value, writer, depth + 2, options)

    for key, value in items[1:]:
        encode_key_value_pair(key, value, writer, depth + 1, options)

