from __future__ import annotations

from ._model import ValueArity
from ._model import _InlineParserData
from ._model import _Invocation


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
