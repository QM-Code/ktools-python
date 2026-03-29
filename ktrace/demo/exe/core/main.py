#!/usr/bin/env python3

from __future__ import annotations

import sys

from pathlib import Path


def _configure_demo_imports() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    workspace_root = repo_root.parent

    for path in (
        repo_root / "src",
        repo_root / "demo",
        workspace_root / "kcli" / "src",
    ):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


_configure_demo_imports()

import kcli
import ktrace

from sdk.alpha import get_trace_logger as get_alpha_trace_logger
from sdk.alpha import test_trace_logging_channels as test_alpha_trace_logging_channels


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)

    logger = ktrace.Logger()

    trace = ktrace.TraceLogger("core")
    trace.addChannel("app", ktrace.Color("BrightCyan"))
    trace.addChannel("startup", ktrace.Color("BrightYellow"))

    logger.addTraceLogger(trace)
    logger.addTraceLogger(get_alpha_trace_logger())

    logger.enableChannel(trace, ".app")
    trace.trace("app", "core initialized local trace channels")

    parser = kcli.Parser()
    parser.addInlineParser(logger.makeInlineParser(trace))
    parser.parseOrExit(len(argv), argv)

    trace.trace("app", "cli processing enabled, use --trace for options")
    trace.trace("startup", "testing imported tracing, use --trace '*.*' to view imported channels")
    test_alpha_trace_logging_channels()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
