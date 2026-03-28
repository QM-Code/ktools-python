from __future__ import annotations

from collections.abc import Sequence

from ._model import HandlerContext
from ._model import ValueArity
from ._model import _AliasBinding
from ._model import _CollectedValues
from ._model import _CommandBinding
from ._model import _InlineParserData
from ._model import _InlineTokenKind
from ._model import _InlineTokenMatch
from ._model import _Invocation
from ._model import _InvocationKind
from ._model import _ParseOutcome
from ._model import _ParserData
from ._normalize import make_error
from ._normalize import starts_with
from ._normalize import throw_cli_error


def is_collectable_follow_on_value_token(value: str) -> bool:
    return not (value and value[0] == "-")


def join_with_spaces(parts: Sequence[str]) -> str:
    return " ".join(parts)


def format_option_error_message(option: str, message: str) -> str:
    if not option:
        return message
    return f"option '{option}': {message}"


def report_error(result: _ParseOutcome, option: str, message: str) -> None:
    if result.ok:
        result.ok = False
        result.error_option = option
        result.error_message = message


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


def print_help(invocation: _Invocation) -> None:
    print(f"\nAvailable --{invocation.root}-* options:")
    max_lhs = 0
    for lhs, _ in invocation.help_rows:
        max_lhs = max(max_lhs, len(lhs))
    if not invocation.help_rows:
        print("  (no options registered)")
    else:
        for lhs, rhs in invocation.help_rows:
            padding = max_lhs - len(lhs) if max_lhs > len(lhs) else 0
            print(f"  {lhs}{' ' * (padding + 2)}{rhs}")
    print()


def consume_index(consumed: list[bool], index: int) -> None:
    if 0 <= index < len(consumed) and not consumed[index]:
        consumed[index] = True


def find_command(
    commands: Sequence[tuple[str, _CommandBinding]],
    command: str,
) -> _CommandBinding | None:
    for existing_command, binding in commands:
        if existing_command == command:
            return binding
    return None


def find_alias_binding(data: _ParserData, token: str) -> _AliasBinding | None:
    for alias in data.aliases:
        if token == alias.alias:
            return alias
    return None


def has_alias_preset_tokens(alias_binding: _AliasBinding | None) -> bool:
    return alias_binding is not None and bool(alias_binding.preset_tokens)


def build_effective_value_tokens(
    alias_binding: _AliasBinding | None,
    collected_parts: Sequence[str],
) -> list[str]:
    if not has_alias_preset_tokens(alias_binding):
        return list(collected_parts)
    return [*alias_binding.preset_tokens, *collected_parts]


def build_help_rows(parser: _InlineParserData) -> list[tuple[str, str]]:
    prefix = f"--{parser.root_name}-"
    rows: list[tuple[str, str]] = []
    if parser.root_value_handler and parser.root_value_description:
        lhs = f"--{parser.root_name}"
        if parser.root_value_placeholder:
            lhs += f" {parser.root_value_placeholder}"
        rows.append((lhs, parser.root_value_description))
    for command, binding in parser.commands:
        lhs = prefix + command
        if binding.expects_value:
            if binding.value_arity is ValueArity.OPTIONAL:
                lhs += " [value]"
            elif binding.value_arity is ValueArity.REQUIRED:
                lhs += " <value>"
        rows.append((lhs, binding.description))
    return rows


def match_inline_token(data: _ParserData, arg: str) -> _InlineTokenMatch:
    for parser in data.inline_parsers:
        root_option = f"--{parser.root_name}"
        if arg == root_option:
            return _InlineTokenMatch(kind=_InlineTokenKind.BARE_ROOT, parser=parser)
        root_dash_prefix = f"{root_option}-"
        if starts_with(arg, root_dash_prefix):
            return _InlineTokenMatch(
                kind=_InlineTokenKind.DASH_OPTION,
                parser=parser,
                suffix=arg[len(root_dash_prefix) :],
            )
    return _InlineTokenMatch()


def schedule_invocation(
    binding: _CommandBinding,
    alias_binding: _AliasBinding | None,
    root: str,
    command: str,
    option_token: str,
    index: int,
    tokens: Sequence[str],
    consumed: list[bool],
    invocations: list[_Invocation],
    result: _ParseOutcome,
) -> int:
    consume_index(consumed, index)
    invocation = _Invocation(root=root, option=option_token, command=command)
    if not binding.expects_value:
        if has_alias_preset_tokens(alias_binding):
            report_error(
                result,
                alias_binding.alias,
                f"alias '{alias_binding.alias}' presets values for option '{option_token}' "
                f"which does not accept values",
            )
            return index
        invocation.kind = _InvocationKind.FLAG
        invocation.flag_handler = binding.flag_handler
        invocations.append(invocation)
        return index
    collected = collect_value_tokens(
        index,
        tokens,
        consumed,
        binding.value_arity is ValueArity.REQUIRED,
    )
    if (
        not collected.has_value
        and not has_alias_preset_tokens(alias_binding)
        and binding.value_arity is ValueArity.REQUIRED
    ):
        report_error(result, option_token, f"option '{option_token}' requires a value")
        return index
    if collected.has_value:
        index = collected.last_index
    invocation.kind = _InvocationKind.VALUE
    invocation.value_handler = binding.value_handler
    invocation.value_tokens = build_effective_value_tokens(alias_binding, collected.parts)
    invocations.append(invocation)
    return index


def schedule_positionals(
    data: _ParserData,
    tokens: Sequence[str],
    consumed: list[bool],
    invocations: list[_Invocation],
) -> None:
    if data.positional_handler is None or len(tokens) <= 1:
        return
    invocation = _Invocation(kind=_InvocationKind.POSITIONAL, positional_handler=data.positional_handler)
    for index in range(1, len(tokens)):
        if consumed[index]:
            continue
        token = tokens[index]
        if not token or token[0] != "-":
            consumed[index] = True
            invocation.value_tokens.append(token)
    if invocation.value_tokens:
        invocations.append(invocation)


def build_parse_tokens(argc: int, argv: Sequence[str]) -> list[str]:
    return ["" if argv[index] is None else str(argv[index]) for index in range(argc)]


class _ParseSession:
    def __init__(self, data: _ParserData, argc: int, argv: Sequence[str]) -> None:
        self._data = data
        self._argc = argc
        self._tokens = build_parse_tokens(argc, argv)
        self._consumed = [False] * argc
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
            if arg[0] == "-" and not starts_with(arg, "--"):
                alias_binding = find_alias_binding(self._data, arg)
                if alias_binding is not None:
                    effective_arg = alias_binding.target_token

            if effective_arg[0] != "-":
                index += 1
                continue
            if effective_arg == "--":
                index += 1
                continue
            if starts_with(effective_arg, "--"):
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
        consume_index(self._consumed, index)
        invocation = _Invocation(root=root, option=option_token, command=command)
        if not binding.expects_value:
            if has_alias_preset_tokens(alias_binding):
                report_error(
                    self._result,
                    alias_binding.alias,
                    f"alias '{alias_binding.alias}' presets values for option '{option_token}' "
                    f"which does not accept values",
                )
                return index
            invocation.kind = _InvocationKind.FLAG
            invocation.flag_handler = binding.flag_handler
            self._invocations.append(invocation)
            return index

        collected = collect_value_tokens(
            index,
            self._tokens,
            self._consumed,
            binding.value_arity is ValueArity.REQUIRED,
        )
        if (
            not collected.has_value
            and not has_alias_preset_tokens(alias_binding)
            and binding.value_arity is ValueArity.REQUIRED
        ):
            report_error(self._result, option_token, f"option '{option_token}' requires a value")
            return index

        if collected.has_value:
            index = collected.last_index
        invocation.kind = _InvocationKind.VALUE
        invocation.value_handler = binding.value_handler
        invocation.value_tokens = build_effective_value_tokens(alias_binding, collected.parts)
        self._invocations.append(invocation)
        return index

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


def parse(data: _ParserData, argc: int, argv: Sequence[str] | None) -> None:
    if argc > 0 and argv is None:
        throw_cli_error(make_error("", "kcli received invalid argv (argc > 0 but argv is null)"))
    if argc <= 0 or argv is None:
        return
    if len(argv) < argc:
        throw_cli_error(make_error("", "kcli received invalid argv (argv shorter than argc)"))
    _ParseSession(data, argc, argv).run()
