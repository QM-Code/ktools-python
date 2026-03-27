from __future__ import annotations

from .common import ensure_repo_paths

ensure_repo_paths(__file__)

import kcli

from .common import print_processing_line


def _parse_int_or_throw(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError("expected an integer") from exc


def _handle_profile(context: kcli.HandlerContext, value: str) -> None:
    print_processing_line(context, value)


def _handle_workers(context: kcli.HandlerContext, value: str) -> None:
    if value:
        _parse_int_or_throw(value)
    print_processing_line(context, value)


def get_inline_parser() -> kcli.InlineParser:
    parser = kcli.InlineParser("--beta")
    parser.setHandler("-profile", _handle_profile, "Select beta runtime profile.")
    parser.setHandler("-workers", _handle_workers, "Set beta worker count.")
    return parser
