from __future__ import annotations

from collections.abc import Sequence

from ._model import HandlerContext
from ._model import _AliasBinding
from ._model import _CommandBinding
from ._model import _InlineParserData
from ._model import _InlineTokenKind
from ._model import _Invocation
from ._model import _InvocationKind
from ._model import _ParseOutcome
from ._model import _ParserData
from ._normalize import make_error
from ._normalize import throw_cli_error
from ._process_help import build_help_rows
from ._process_help import print_help
from ._process_plan import build_parse_tokens
from ._process_plan import consume_index
from ._process_plan import find_alias_binding
from ._process_plan import find_command
from ._process_plan import format_option_error_message
from ._process_plan import match_inline_token
from ._process_plan import report_error
from ._process_plan import schedule_invocation
from ._process_plan import schedule_positionals
from ._process_values import build_effective_value_tokens
from ._process_values import collect_value_tokens
from ._process_values import has_alias_preset_tokens
from ._process_values import join_with_spaces


class _ParseSession:
    def __init__(self, data: _ParserData, argv: Sequence[str]) -> None:
        self._data = data
        self._argc = len(argv)
        self._tokens = build_parse_tokens(self._argc, argv)
        self._consumed = [False] * self._argc
        self._invocations: list[_Invocation] = []
        self._result = _ParseOutcome()

    def run(self) -> None:
        self._scan_tokens()
        if self._result.ok:
            self._schedule_positionals()
        if self._result.ok:
            self._report_unknown_options()
        if self._result.ok:
            self._execute_invocations()
        if not self._result.ok:
            throw_cli_error(self._result)

    def _scan_tokens(self) -> None:
        index = 1
        while index < self._argc:
            if self._consumed[index]:
                index += 1
                continue

            arg = self._tokens[index]
            if not arg:
                index += 1
                continue

            alias_binding: _AliasBinding | None = None
            effective_arg = arg
            if arg[0] == "-" and not arg.startswith("--"):
                alias_binding = find_alias_binding(self._data, arg)
                if alias_binding is not None:
                    effective_arg = alias_binding.target_token

            if effective_arg[0] != "-":
                index += 1
                continue
            if effective_arg == "--":
                index += 1
                continue
            if effective_arg.startswith("--"):
                index = self._handle_double_dash_option(index, effective_arg, alias_binding)

            if not self._result.ok:
                return
            index += 1

    def _handle_double_dash_option(
        self,
        index: int,
        effective_arg: str,
        alias_binding: _AliasBinding | None,
    ) -> int:
        inline_match = match_inline_token(self._data, effective_arg)
        if inline_match.kind is _InlineTokenKind.BARE_ROOT:
            return self._handle_bare_inline_root(index, effective_arg, inline_match.parser, alias_binding)

        if inline_match.kind is _InlineTokenKind.DASH_OPTION:
            binding = find_command(inline_match.parser.commands, inline_match.suffix)
            if inline_match.suffix and binding is not None:
                return self._schedule_invocation(
                    binding,
                    alias_binding,
                    inline_match.parser.root_name,
                    inline_match.suffix,
                    effective_arg,
                    index,
                )
            return index

        command = effective_arg[2:]
        binding = find_command(self._data.commands, command)
        if binding is None:
            return index
        return self._schedule_invocation(
            binding,
            alias_binding,
            "",
            command,
            effective_arg,
            index,
        )

    def _handle_bare_inline_root(
        self,
        index: int,
        option_token: str,
        parser: _InlineParserData,
        alias_binding: _AliasBinding | None,
    ) -> int:
        consume_index(self._consumed, index)
        collected = collect_value_tokens(index, self._tokens, self._consumed, False)
        if not collected.has_value and not has_alias_preset_tokens(alias_binding):
            self._invocations.append(
                _Invocation(
                    kind=_InvocationKind.PRINT_HELP,
                    root=parser.root_name,
                    help_rows=build_help_rows(parser),
                )
            )
            return index

        if parser.root_value_handler is None:
            report_error(self._result, option_token, f"unknown value for option '{option_token}'")
            return index

        self._invocations.append(
            _Invocation(
                kind=_InvocationKind.VALUE,
                root=parser.root_name,
                option=option_token,
                value_handler=parser.root_value_handler,
                value_tokens=build_effective_value_tokens(alias_binding, collected.parts),
            )
        )
        if collected.has_value:
            return collected.last_index
        return index

    def _schedule_invocation(
        self,
        binding: _CommandBinding,
        alias_binding: _AliasBinding | None,
        root: str,
        command: str,
        option_token: str,
        index: int,
    ) -> int:
        return schedule_invocation(
            binding,
            alias_binding,
            root,
            command,
            option_token,
            index,
            self._tokens,
            self._consumed,
            self._invocations,
            self._result,
        )

    def _schedule_positionals(self) -> None:
        schedule_positionals(self._data, self._tokens, self._consumed, self._invocations)

    def _report_unknown_options(self) -> None:
        for index in range(1, self._argc):
            if self._consumed[index]:
                continue
            token = self._tokens[index]
            if token and token[0] == "-":
                report_error(self._result, token, f"unknown option {token}")
                return

    def _execute_invocations(self) -> None:
        for invocation in self._invocations:
            if not self._result.ok:
                return
            if invocation.kind is _InvocationKind.PRINT_HELP:
                print_help(invocation)
                continue

            context = HandlerContext(
                root=invocation.root,
                option=invocation.option,
                command=invocation.command,
                value_tokens=list(invocation.value_tokens),
            )
            try:
                if invocation.kind is _InvocationKind.FLAG:
                    assert invocation.flag_handler is not None
                    invocation.flag_handler(context)
                elif invocation.kind is _InvocationKind.VALUE:
                    assert invocation.value_handler is not None
                    invocation.value_handler(context, join_with_spaces(invocation.value_tokens))
                elif invocation.kind is _InvocationKind.POSITIONAL:
                    assert invocation.positional_handler is not None
                    invocation.positional_handler(context)
            except Exception as exc:
                report_error(
                    self._result,
                    invocation.option,
                    format_option_error_message(invocation.option, str(exc)),
                )
            except BaseException:
                report_error(
                    self._result,
                    invocation.option,
                    format_option_error_message(
                        invocation.option,
                        "unknown exception while handling option",
                    ),
                )


def parse(data: _ParserData, argv: Sequence[str] | None) -> None:
    if argv is None:
        return
    if len(argv) == 0:
        return
    _ParseSession(data, argv).run()
