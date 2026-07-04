"""Small Python 3.10 fallback for the subset of TOML used by local tools."""

from __future__ import annotations

import re
from typing import Any, BinaryIO


class TOMLDecodeError(ValueError):
    pass


_ARRAY_TABLE_RE = re.compile(r"^\s*\[\[\s*([A-Za-z0-9_.-]+)\s*\]\]\s*(?:#.*)?$")
_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*=")


def load(fp: BinaryIO) -> dict[str, Any]:
    data = fp.read()
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return loads(data)


def loads(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current: dict[str, Any] = result
    multiline_delimiter: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if multiline_delimiter is not None:
            if multiline_delimiter in line:
                multiline_delimiter = None
            continue
        if not line or line.startswith("#"):
            continue

        table_match = _ARRAY_TABLE_RE.match(line)
        if table_match:
            table_name = table_match.group(1)
            table: dict[str, Any] = {}
            result.setdefault(table_name, []).append(table)
            current = table
            continue

        key_match = _KEY_RE.match(line)
        if not key_match:
            continue

        key = key_match.group(1)
        value_text = line[key_match.end() :].strip()
        if value_text.startswith(('"""', "'''")):
            delimiter = value_text[:3]
            remainder = value_text[3:]
            if delimiter not in remainder:
                multiline_delimiter = delimiter
            current[key] = remainder.split(delimiter, 1)[0]
            continue

        current[key] = _parse_value(value_text)

    return result


def _parse_value(value_text: str) -> Any:
    if not value_text:
        return ""

    quote = value_text[0]
    if quote in {"'", '"'}:
        value, _ = _parse_quoted_string(value_text, quote)
        return value

    bare = value_text.split("#", 1)[0].strip()
    if bare.lower() == "true":
        return True
    if bare.lower() == "false":
        return False
    return bare


def _parse_quoted_string(value_text: str, quote: str) -> tuple[str, int]:
    characters: list[str] = []
    escaped = False

    for index, character in enumerate(value_text[1:], start=1):
        if escaped:
            characters.append(_unescape(character))
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if character == quote:
            return "".join(characters), index + 1
        characters.append(character)

    raise TOMLDecodeError("Unterminated string")


def _unescape(character: str) -> str:
    escapes = {
        "b": "\b",
        "t": "\t",
        "n": "\n",
        "f": "\f",
        "r": "\r",
        '"': '"',
        "\\": "\\",
    }
    return escapes.get(character, character)
