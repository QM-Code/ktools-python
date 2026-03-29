from __future__ import annotations

from collections.abc import Sequence

from ._model import _AliasBinding
from ._model import _CommandBinding
from ._model import _InlineParserData
from ._model import _InlineTokenKind
from ._model import _InlineTokenMatch
from ._model import _Invocation
from ._model import _InvocationKind
from ._model import _ParseOutcome
from ._model import _ParserData
from ._model import ValueArity
from ._normalize import starts_with
from ._process_values import build_effective_value_tokens
from ._process_values import collect_value_tokens
from ._process_values import has_alias_preset_tokens


def format_option_error_message(option: str, message: str) -> str:
    if not option:
        return message
    return f"option '{option}': {message}"


def report_error(result: _ParseOutcome, option: str, message: str) -> None:
    if result.ok:
        result.ok = False
        result.error_option = option
        result.error_message = message


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
            assert alias_binding is not None
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

    invocation = _Invocation(
        kind=_InvocationKind.POSITIONAL,
        positional_handler=data.positional_handler,
    )
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
