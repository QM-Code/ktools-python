from __future__ import annotations

import sys

from pathlib import Path


def _ensure_repo_paths(current_file: str) -> None:
    file_path = Path(current_file).resolve()
    repo_root: Path | None = None
    for parent in file_path.parents:
        if (parent / "src").is_dir() and (parent / "demo").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError("unable to locate repository root for alpha demo")

    demo_root = repo_root / "demo"
    src_root = repo_root / "src"
    for path in (str(src_root), str(demo_root)):
        if path not in sys.path:
            sys.path.insert(0, path)


_ensure_repo_paths(__file__)

import kcli


def _print_processing_line(context: kcli.HandlerContext, value: str) -> None:
    if not context.value_tokens:
        print(f"Processing {context.option}")
        return
    if len(context.value_tokens) == 1:
        print(f'Processing {context.option} with value "{value}"')
        return
    joined = ",".join(f'"{token}"' for token in context.value_tokens)
    print(f"Processing {context.option} with values [{joined}]")


def _handle_message(context: kcli.HandlerContext, value: str) -> None:
    _print_processing_line(context, value)


def _handle_enable(context: kcli.HandlerContext, value: str) -> None:
    _print_processing_line(context, value)


def get_inline_parser() -> kcli.InlineParser:
    parser = kcli.InlineParser("--alpha")
    parser.set_handler("-message", _handle_message, "Set alpha message label.")
    parser.set_optional_value_handler("-enable", _handle_enable, "Enable alpha processing.")
    return parser
