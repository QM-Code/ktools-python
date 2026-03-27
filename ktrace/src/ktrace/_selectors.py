from __future__ import annotations

import re

from dataclasses import dataclass


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class _SegmentPattern:
    kind: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class SelectorPattern:
    text: str
    segments: tuple[_SegmentPattern, ...]


def validate_identifier_or_throw(value: str, what: str) -> str:
    token = str(value).strip()
    if not _IDENTIFIER_RE.fullmatch(token):
        raise ValueError(f"invalid trace {what} '{token}'")
    return token


def normalize_channel_or_throw(channel: str) -> str:
    token = str(channel).strip()
    if not token:
        raise ValueError("invalid trace channel ''")

    parts = token.split(".")
    if any(not part for part in parts):
        raise ValueError(f"invalid trace channel '{token}'")
    for part in parts:
        validate_identifier_or_throw(part, "channel")
    return token


def normalize_namespace_or_throw(trace_namespace: str) -> str:
    return validate_identifier_or_throw(trace_namespace, "namespace")


def split_csv_preserving_braces(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0

    for char in text:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                raise ValueError("Invalid trace selector: unmatched '}'")
        elif char == "," and depth == 0:
            item = "".join(current).strip()
            if not item:
                raise ValueError("trace selector list must not be empty")
            items.append(item)
            current = []
            continue
        current.append(char)

    if depth != 0:
        raise ValueError("Invalid trace selector: unmatched '{'")

    item = "".join(current).strip()
    if not item:
        raise ValueError("trace selector list must not be empty")
    items.append(item)
    return items


def _parse_segment_or_throw(segment: str) -> _SegmentPattern:
    token = segment.strip()
    if not token:
        raise ValueError("Invalid trace selector: empty selector segment")
    if token == "*":
        return _SegmentPattern("wildcard", ())
    if token.startswith("{") or token.endswith("}"):
        if not (token.startswith("{") and token.endswith("}")):
            raise ValueError(f"Invalid trace selector: '{segment}'")
        inner = token[1:-1].strip()
        if not inner:
            raise ValueError(f"Invalid trace selector: '{segment}'")
        values = tuple(validate_identifier_or_throw(item.strip(), "selector") for item in inner.split(","))
        return _SegmentPattern("set", values)
    return _SegmentPattern("exact", (validate_identifier_or_throw(token, "selector"),))


def parse_selector_or_throw(raw_selector: str, local_namespace: str = "") -> SelectorPattern:
    selector = str(raw_selector).strip()
    if not selector:
        raise ValueError("trace selector list must not be empty")
    if selector == "*":
        raise ValueError("Invalid trace selector: '*' (did you mean '.*'?)")

    resolved = selector
    if selector.startswith("."):
        namespace = normalize_namespace_or_throw(local_namespace)
        resolved = f"{namespace}{selector}"

    parts = resolved.split(".")
    if len(parts) < 2 or any(not part for part in parts):
        raise ValueError(f"Invalid trace selector: '{selector}'")

    segments = tuple(_parse_segment_or_throw(part) for part in parts)
    return SelectorPattern(text=resolved, segments=segments)


def matches_selector(pattern: SelectorPattern, qualified_channel: str) -> bool:
    candidate = qualified_channel.split(".")
    if len(candidate) > len(pattern.segments):
        return False

    for index, segment in enumerate(pattern.segments):
        if index >= len(candidate):
            return all(trailing.kind == "wildcard" for trailing in pattern.segments[index:])

        value = candidate[index]
        if segment.kind == "wildcard":
            continue
        if segment.kind == "set":
            if value not in segment.values:
                return False
            continue
        if value != segment.values[0]:
            return False

    return len(candidate) <= len(pattern.segments)
