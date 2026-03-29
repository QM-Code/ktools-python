from __future__ import annotations

from collections.abc import Sequence

from ._model import _AliasBinding
from ._model import _CollectedValues


def is_collectable_follow_on_value_token(value: str) -> bool:
    return not (value and value[0] == "-")


def collect_value_tokens(
    option_index: int,
    tokens: Sequence[str],
    consumed: list[bool],
    allow_option_like_first_value: bool,
) -> _CollectedValues:
    collected = _CollectedValues(last_index=option_index)
    first_value_index = option_index + 1
    has_next = 0 <= first_value_index < len(tokens) and not consumed[first_value_index]
    if not has_next:
        return collected

    first = tokens[first_value_index]
    if not allow_option_like_first_value and first and first[0] == "-":
        return collected

    collected.has_value = True
    collected.parts.append(first)
    consumed[first_value_index] = True
    collected.last_index = first_value_index

    if allow_option_like_first_value and first and first[0] == "-":
        return collected

    for scan in range(first_value_index + 1, len(tokens)):
        if consumed[scan]:
            continue
        next_token = tokens[scan]
        if not is_collectable_follow_on_value_token(next_token):
            break
        collected.parts.append(next_token)
        consumed[scan] = True
        collected.last_index = scan
    return collected


def has_alias_preset_tokens(alias_binding: _AliasBinding | None) -> bool:
    return alias_binding is not None and bool(alias_binding.preset_tokens)


def build_effective_value_tokens(
    alias_binding: _AliasBinding | None,
    collected_parts: Sequence[str],
) -> list[str]:
    if not has_alias_preset_tokens(alias_binding):
        return list(collected_parts)
    return [*alias_binding.preset_tokens, *collected_parts]


def join_with_spaces(parts: Sequence[str]) -> str:
    return " ".join(parts)
