from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Callable


@dataclass
class HandlerContext:
    root: str = ""
    option: str = ""
    command: str = ""
    value_tokens: list[str] = field(default_factory=list)


class CliError(RuntimeError):
    def __init__(self, option: str, message: str) -> None:
        super().__init__(message if message else "kcli parse failed")
        self._option = option

    def option(self) -> str:
        return self._option


FlagHandler = Callable[[HandlerContext], None]
ValueHandler = Callable[[HandlerContext, str], None]
PositionalHandler = Callable[[HandlerContext], None]


class ValueArity(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass
class _CommandBinding:
    expects_value: bool = False
    flag_handler: FlagHandler | None = None
    value_handler: ValueHandler | None = None
    value_arity: ValueArity = ValueArity.REQUIRED
    description: str = ""


@dataclass
class _AliasBinding:
    alias: str = ""
    target_token: str = ""
    preset_tokens: list[str] = field(default_factory=list)


@dataclass
class _InlineParserData:
    root_name: str = ""
    root_value_handler: ValueHandler | None = None
    root_value_placeholder: str = ""
    root_value_description: str = ""
    commands: list[tuple[str, _CommandBinding]] = field(default_factory=list)


@dataclass
class _ParserData:
    positional_handler: PositionalHandler | None = None
    aliases: list[_AliasBinding] = field(default_factory=list)
    commands: list[tuple[str, _CommandBinding]] = field(default_factory=list)
    inline_parsers: list[_InlineParserData] = field(default_factory=list)


@dataclass
class _ParseOutcome:
    ok: bool = True
    error_option: str = ""
    error_message: str = ""


@dataclass
class _CollectedValues:
    has_value: bool = False
    parts: list[str] = field(default_factory=list)
    last_index: int = -1


class _InvocationKind(Enum):
    FLAG = "flag"
    VALUE = "value"
    POSITIONAL = "positional"
    PRINT_HELP = "print_help"


@dataclass
class _Invocation:
    kind: _InvocationKind = _InvocationKind.FLAG
    root: str = ""
    option: str = ""
    command: str = ""
    value_tokens: list[str] = field(default_factory=list)
    flag_handler: FlagHandler | None = None
    value_handler: ValueHandler | None = None
    positional_handler: PositionalHandler | None = None
    help_rows: list[tuple[str, str]] = field(default_factory=list)


class _InlineTokenKind(Enum):
    NONE = "none"
    BARE_ROOT = "bare_root"
    DASH_OPTION = "dash_option"


@dataclass
class _InlineTokenMatch:
    kind: _InlineTokenKind = _InlineTokenKind.NONE
    parser: _InlineParserData | None = None
    suffix: str = ""
