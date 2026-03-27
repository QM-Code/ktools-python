#!/usr/bin/env python3

from __future__ import annotations

import sys

from pathlib import Path


def _find_demo_root() -> Path:
    file_path = Path(__file__).resolve()
    for parent in file_path.parents:
        if (parent / "sdk").is_dir() and (parent / "tests").is_dir():
            return parent
    raise RuntimeError("unable to locate demo root")


DEMO_ROOT = _find_demo_root()
if str(DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEMO_ROOT))

from sdk.common import ensure_workspace_paths

ensure_workspace_paths(__file__)

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
