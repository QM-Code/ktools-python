from __future__ import annotations

from .common import ensure_repo_paths

ensure_repo_paths(__file__)

import kcli

from .common import print_processing_line


def _handle_message(context: kcli.HandlerContext, value: str) -> None:
    print_processing_line(context, value)


def _handle_enable(context: kcli.HandlerContext, value: str) -> None:
    print_processing_line(context, value)


def get_inline_parser() -> kcli.InlineParser:
    parser = kcli.InlineParser("--alpha")
    parser.setHandler("-message", _handle_message, "Set alpha message label.")
    parser.setOptionalValueHandler("-enable", _handle_enable, "Enable alpha processing.")
    return parser
