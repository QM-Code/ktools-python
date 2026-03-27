from __future__ import annotations

import inspect
import sys

from typing import Callable

from ._model import CliError
from ._model import _ParseOutcome


def report_cli_error_and_exit(message: str) -> None:
    if sys.stderr.isatty():
        sys.stderr.write(f"[\x1b[31merror\x1b[0m] [\x1b[94mcli\x1b[0m] {message}\n")
    else:
        sys.stderr.write(f"[error] [cli] {message}\n")
    sys.stderr.flush()
    raise SystemExit(2)


def trim_whitespace(value: str) -> str:
    return value.strip()


def contains_whitespace(value: str) -> bool:
    return any(char.isspace() for char in value)


def starts_with(value: str, prefix: str) -> bool:
    return value.startswith(prefix)


def normalize_root_name_or_throw(raw_root: str) -> str:
    root = trim_whitespace(str(raw_root))
    if not root:
        raise ValueError("kcli root must not be empty")
    if root[0] == "-":
        raise ValueError("kcli root must not begin with '-'")
    if contains_whitespace(root):
        raise ValueError("kcli root is invalid")
    return root


def normalize_inline_root_option_or_throw(raw_root: str) -> str:
    root = trim_whitespace(str(raw_root))
    if not root:
        raise ValueError("kcli root must not be empty")
    if starts_with(root, "--"):
        root = root[2:]
    elif root[0] == "-":
        raise ValueError("kcli root must use '--root' or 'root'")
    return normalize_root_name_or_throw(root)


def normalize_inline_handler_option_or_throw(raw_option: str, root_name: str) -> str:
    option = trim_whitespace(str(raw_option))
    if not option:
        raise ValueError("kcli inline handler option must not be empty")
    if starts_with(option, "--"):
        full_prefix = f"--{root_name}-"
        if not starts_with(option, full_prefix):
            raise ValueError(
                f"kcli inline handler option must use '-name' or '{full_prefix}name'"
            )
        option = option[len(full_prefix) :]
    elif option[0] == "-":
        option = option[1:]
    else:
        raise ValueError(
            f"kcli inline handler option must use '-name' or '--{root_name}-name'"
        )
    if not option:
        raise ValueError("kcli command must not be empty")
    if option[0] == "-":
        raise ValueError("kcli command must not start with '-'")
    if contains_whitespace(option):
        raise ValueError("kcli command must not contain whitespace")
    return option


def normalize_primary_handler_option_or_throw(raw_option: str) -> str:
    option = trim_whitespace(str(raw_option))
    if not option:
        raise ValueError("kcli end-user handler option must not be empty")
    if starts_with(option, "--"):
        option = option[2:]
    elif option[0] == "-":
        raise ValueError("kcli end-user handler option must use '--name' or 'name'")
    if not option:
        raise ValueError("kcli command must not be empty")
    if option[0] == "-":
        raise ValueError("kcli command must not start with '-'")
    if contains_whitespace(option):
        raise ValueError("kcli command must not contain whitespace")
    return option


def normalize_alias_or_throw(raw_alias: str) -> str:
    alias = trim_whitespace(str(raw_alias))
    if len(alias) < 2 or alias[0] != "-" or starts_with(alias, "--") or contains_whitespace(alias):
        raise ValueError("kcli alias must use single-dash form, e.g. '-v'")
    return alias


def normalize_alias_target_option_or_throw(raw_target: str) -> str:
    target = trim_whitespace(str(raw_target))
    if len(target) < 3 or not starts_with(target, "--") or contains_whitespace(target):
        raise ValueError("kcli alias target must use double-dash form, e.g. '--verbose'")
    if target[2] == "-":
        raise ValueError("kcli alias target must use double-dash form, e.g. '--verbose'")
    return target


def normalize_help_placeholder_or_throw(raw_placeholder: str) -> str:
    placeholder = trim_whitespace(str(raw_placeholder))
    if not placeholder:
        raise ValueError("kcli help placeholder must not be empty")
    return placeholder


def normalize_description_or_throw(raw_description: str) -> str:
    description = trim_whitespace(str(raw_description))
    if not description:
        raise ValueError("kcli command description must not be empty")
    return description


def make_error(option: str, message: str) -> _ParseOutcome:
    return _ParseOutcome(ok=False, error_option=option, error_message=message)


def throw_cli_error(result: _ParseOutcome) -> None:
    if result.ok:
        raise RuntimeError("kcli internal error: ThrowCliError called without a failure")
    raise CliError(result.error_option, result.error_message)


def inspect_callable_arity(handler: Callable[..., None]) -> tuple[int, int | None]:
    signature = inspect.signature(handler)
    minimum = 0
    maximum = 0
    has_varargs = False
    for parameter in signature.parameters.values():
        if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            maximum += 1
            if parameter.default is inspect._empty:
                minimum += 1
        elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            has_varargs = True
    return minimum, None if has_varargs else maximum


def validate_handler_arity(handler: Callable[..., None] | None, minimum: int, empty_message: str) -> None:
    if handler is None:
        raise ValueError(empty_message)
    min_args, max_args = inspect_callable_arity(handler)
    if max_args is not None and max_args < minimum:
        raise ValueError(empty_message)
    if min_args > minimum:
        raise ValueError(empty_message)


def classify_set_handler(handler: Callable[..., None] | None) -> str:
    if handler is None:
        raise ValueError("kcli handler must not be empty")
    min_args, max_args = inspect_callable_arity(handler)
    can_take_one = min_args <= 1 and (max_args is None or max_args >= 1)
    can_take_two = min_args <= 2 and (max_args is None or max_args >= 2)
    if can_take_two:
        return "value"
    if can_take_one:
        return "flag"
    raise ValueError("kcli handler must not be empty")
