from __future__ import annotations

import copy

from collections.abc import Iterable

from ._model import FlagHandler
from ._model import PositionalHandler
from ._model import ValueArity
from ._model import ValueHandler
from ._model import _AliasBinding
from ._model import _CommandBinding
from ._model import _InlineParserData
from ._model import _ParserData
from ._normalize import normalize_alias_or_throw
from ._normalize import normalize_alias_target_option_or_throw
from ._normalize import normalize_description_or_throw
from ._normalize import normalize_help_placeholder_or_throw
from ._normalize import normalize_inline_handler_option_or_throw
from ._normalize import normalize_inline_root_option_or_throw
from ._normalize import normalize_primary_handler_option_or_throw
from ._normalize import validate_handler_arity


def clone_inline_parser_data(data: _InlineParserData) -> _InlineParserData:
    return _InlineParserData(
        root_name=data.root_name,
        root_value_handler=data.root_value_handler,
        root_value_placeholder=data.root_value_placeholder,
        root_value_description=data.root_value_description,
        commands=[(name, copy.copy(binding)) for name, binding in data.commands],
    )


def make_flag_binding(handler: FlagHandler, description: str) -> _CommandBinding:
    validate_handler_arity(handler, 1, "kcli flag handler must not be empty")
    return _CommandBinding(
        expects_value=False,
        flag_handler=handler,
        description=normalize_description_or_throw(description),
    )


def make_value_binding(handler: ValueHandler, description: str, arity: ValueArity) -> _CommandBinding:
    validate_handler_arity(handler, 2, "kcli value handler must not be empty")
    return _CommandBinding(
        expects_value=True,
        value_handler=handler,
        value_arity=arity,
        description=normalize_description_or_throw(description),
    )


def upsert_command(
    commands: list[tuple[str, _CommandBinding]],
    command: str,
    binding: _CommandBinding,
) -> None:
    for index, (existing_command, _) in enumerate(commands):
        if existing_command != command:
            continue
        commands[index] = (command, binding)
        return
    commands.append((command, binding))


def register_command(
    commands: list[tuple[str, _CommandBinding]],
    command: str,
    handler: FlagHandler | ValueHandler,
    description: str,
    value_arity: ValueArity | None,
) -> None:
    if value_arity is None:
        upsert_command(commands, command, make_flag_binding(handler, description))
        return
    upsert_command(commands, command, make_value_binding(handler, description, value_arity))


def set_inline_root(data: _InlineParserData, root: str) -> None:
    data.root_name = normalize_inline_root_option_or_throw(root)


def set_root_value_handler(data: _InlineParserData, handler: ValueHandler) -> None:
    validate_handler_arity(handler, 2, "kcli root value handler must not be empty")
    data.root_value_handler = handler
    data.root_value_placeholder = ""
    data.root_value_description = ""


def set_root_value_handler_with_help(
    data: _InlineParserData,
    handler: ValueHandler,
    value_placeholder: str,
    description: str,
) -> None:
    validate_handler_arity(handler, 2, "kcli root value handler must not be empty")
    data.root_value_handler = handler
    data.root_value_placeholder = normalize_help_placeholder_or_throw(value_placeholder)
    data.root_value_description = normalize_description_or_throw(description)


def set_inline_handler_flag(
    data: _InlineParserData,
    option: str,
    handler: FlagHandler,
    description: str,
) -> None:
    command = normalize_inline_handler_option_or_throw(option, data.root_name)
    register_command(data.commands, command, handler, description, None)


def set_inline_handler_value(
    data: _InlineParserData,
    option: str,
    handler: ValueHandler,
    description: str,
) -> None:
    command = normalize_inline_handler_option_or_throw(option, data.root_name)
    register_command(data.commands, command, handler, description, ValueArity.REQUIRED)


def set_inline_optional_value_handler(
    data: _InlineParserData,
    option: str,
    handler: ValueHandler,
    description: str,
) -> None:
    command = normalize_inline_handler_option_or_throw(option, data.root_name)
    register_command(data.commands, command, handler, description, ValueArity.OPTIONAL)


def set_alias(
    data: _ParserData,
    alias: str,
    target: str,
    preset_tokens: Iterable[str],
) -> None:
    normalized_alias = normalize_alias_or_throw(alias)
    normalized_target = normalize_alias_target_option_or_throw(target)
    normalized_binding = _AliasBinding(
        alias=normalized_alias,
        target_token=normalized_target,
        preset_tokens=[str(token) for token in preset_tokens],
    )
    for index, binding in enumerate(data.aliases):
        if binding.alias != normalized_alias:
            continue
        data.aliases[index] = normalized_binding
        return
    data.aliases.append(normalized_binding)


def set_primary_handler_flag(
    data: _ParserData,
    option: str,
    handler: FlagHandler,
    description: str,
) -> None:
    command = normalize_primary_handler_option_or_throw(option)
    register_command(data.commands, command, handler, description, None)


def set_primary_handler_value(
    data: _ParserData,
    option: str,
    handler: ValueHandler,
    description: str,
) -> None:
    command = normalize_primary_handler_option_or_throw(option)
    register_command(data.commands, command, handler, description, ValueArity.REQUIRED)


def set_primary_optional_value_handler(
    data: _ParserData,
    option: str,
    handler: ValueHandler,
    description: str,
) -> None:
    command = normalize_primary_handler_option_or_throw(option)
    register_command(data.commands, command, handler, description, ValueArity.OPTIONAL)


def set_positional_handler(data: _ParserData, handler: PositionalHandler) -> None:
    validate_handler_arity(handler, 1, "kcli positional handler must not be empty")
    data.positional_handler = handler


def add_inline_parser(data: _ParserData, parser: _InlineParserData) -> None:
    for existing in data.inline_parsers:
        if existing.root_name != parser.root_name:
            continue
        raise ValueError(f"kcli inline parser root '--{parser.root_name}' is already registered")
    data.inline_parsers.append(parser)
