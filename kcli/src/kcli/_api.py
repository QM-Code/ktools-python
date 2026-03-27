from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sequence
from typing import Callable

from ._backend import add_inline_parser
from ._backend import clone_inline_parser_data
from ._backend import set_alias
from ._backend import set_inline_handler_flag
from ._backend import set_inline_handler_value
from ._backend import set_inline_optional_value_handler
from ._backend import set_inline_root
from ._backend import set_positional_handler
from ._backend import set_primary_handler_flag
from ._backend import set_primary_handler_value
from ._backend import set_primary_optional_value_handler
from ._backend import set_root_value_handler
from ._backend import set_root_value_handler_with_help
from ._model import CliError
from ._model import HandlerContext
from ._model import PositionalHandler
from ._model import ValueHandler
from ._model import _InlineParserData
from ._model import _ParserData
from ._normalize import classify_set_handler
from ._normalize import report_cli_error_and_exit
from ._normalize import validate_handler_arity
from ._process import parse


class InlineParser:
    def __init__(self, root: str) -> None:
        self._data = _InlineParserData()
        set_inline_root(self._data, root)

    def setRoot(self, root: str) -> None:
        set_inline_root(self._data, root)

    def setRootValueHandler(
        self,
        handler: ValueHandler,
        value_placeholder: str | None = None,
        description: str | None = None,
    ) -> None:
        if value_placeholder is None and description is None:
            set_root_value_handler(self._data, handler)
            return
        if value_placeholder is None or description is None:
            raise ValueError(
                "kcli root value handler help metadata requires both a placeholder and description"
            )
        set_root_value_handler_with_help(self._data, handler, value_placeholder, description)

    def setHandler(self, option: str, handler: Callable[..., None], description: str) -> None:
        kind = classify_set_handler(handler)
        if kind == "flag":
            set_inline_handler_flag(self._data, option, handler, description)
            return
        set_inline_handler_value(self._data, option, handler, description)

    def setOptionalValueHandler(self, option: str, handler: ValueHandler, description: str) -> None:
        validate_handler_arity(handler, 2, "kcli value handler must not be empty")
        set_inline_optional_value_handler(self._data, option, handler, description)


class Parser:
    def __init__(self) -> None:
        self._data = _ParserData()

    def addAlias(
        self,
        alias: str,
        target: str,
        preset_tokens: Iterable[str] | None = None,
    ) -> None:
        set_alias(self._data, alias, target, preset_tokens or ())

    def setHandler(self, option: str, handler: Callable[..., None], description: str) -> None:
        kind = classify_set_handler(handler)
        if kind == "flag":
            set_primary_handler_flag(self._data, option, handler, description)
            return
        set_primary_handler_value(self._data, option, handler, description)

    def setOptionalValueHandler(self, option: str, handler: ValueHandler, description: str) -> None:
        validate_handler_arity(handler, 2, "kcli value handler must not be empty")
        set_primary_optional_value_handler(self._data, option, handler, description)

    def setPositionalHandler(self, handler: PositionalHandler) -> None:
        set_positional_handler(self._data, handler)

    def addInlineParser(self, parser: InlineParser) -> None:
        add_inline_parser(self._data, clone_inline_parser_data(parser._data))

    def parseOrExit(self, argc: int, argv: Sequence[str] | None) -> None:
        try:
            self.parseOrThrow(argc, argv)
        except CliError as exc:
            report_cli_error_and_exit(str(exc))

    def parseOrThrow(self, argc: int, argv: Sequence[str] | None) -> None:
        parse(self._data, argc, argv)


__all__ = [
    "CliError",
    "HandlerContext",
    "InlineParser",
    "Parser",
]
