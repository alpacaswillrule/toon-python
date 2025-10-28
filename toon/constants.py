"""Constant values and delimiter definitions for the TOON encoder."""

from __future__ import annotations

# Region: list markers
LIST_ITEM_MARKER = "-"
LIST_ITEM_PREFIX = "- "

# Region: structural characters
COMMA = ","
COLON = ":"
SPACE = " "
PIPE = "|"

# Region: brackets and braces
OPEN_BRACKET = "["
CLOSE_BRACKET = "]"
OPEN_BRACE = "{"
CLOSE_BRACE = "}"

# Region: literals
NULL_LITERAL = "null"
TRUE_LITERAL = "true"
FALSE_LITERAL = "false"

# Region: escape characters
BACKSLASH = "\\"
DOUBLE_QUOTE = '"'
NEWLINE = "\n"
CARRIAGE_RETURN = "\r"
TAB = "\t"

# Region: delimiters
DELIMITERS = {
    "comma": COMMA,
    "tab": TAB,
    "pipe": PIPE,
}

DelimiterKey = str
Delimiter = str

DEFAULT_DELIMITER: Delimiter = DELIMITERS["comma"]

