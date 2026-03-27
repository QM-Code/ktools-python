from __future__ import annotations

from .common import ensure_repo_paths

ensure_repo_paths(__file__)

import kcli

from .common import print_processing_line


def _handle_strict(context: kcli.HandlerContext, value: str) -> None:
    print_processing_line(context, value)


def _handle_tag(context: kcli.HandlerContext, value: str) -> None:
    print_processing_line(context, value)


def get_inline_parser() -> kcli.InlineParser:
    parser = kcli.InlineParser("--gamma")
    parser.setOptionalValueHandler("-strict", _handle_strict, "Enable strict gamma mode.")
    parser.setHandler("-tag", _handle_tag, "Set a gamma tag label.")
    return parser
