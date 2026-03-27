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
from sdk.beta import get_trace_logger as get_beta_trace_logger
from sdk.beta import test_trace_logging_channels as test_beta_trace_logging_channels
from sdk.gamma import get_trace_logger as get_gamma_trace_logger
from sdk.gamma import test_trace_logging_channels as test_gamma_trace_logging_channels


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)

    logger = ktrace.Logger()

    trace = ktrace.TraceLogger("omega")
    trace.addChannel("app", ktrace.Color("BrightCyan"))
    trace.addChannel("orchestrator", ktrace.Color("BrightYellow"))
    trace.addChannel("deep")
    trace.addChannel("deep.branch")
    trace.addChannel("deep.branch.leaf", ktrace.Color("LightSalmon1"))

    logger.addTraceLogger(trace)
    logger.addTraceLogger(get_alpha_trace_logger())
    logger.addTraceLogger(get_beta_trace_logger())
    logger.addTraceLogger(get_gamma_trace_logger())

    logger.enableChannel(trace, ".app")
    trace.trace("app", "omega initialized local trace channels")
    logger.disableChannel(trace, ".app")

    parser = kcli.Parser()
    parser.addInlineParser(logger.makeInlineParser(trace))
    parser.parseOrExit(len(argv), argv)

    trace.trace("app", "cli processing enabled, use --trace for options")
    trace.trace("app", "testing external tracing, use --trace '*.*' to view top-level channels")
    trace.trace("deep.branch.leaf", "omega trace test on channel 'deep.branch.leaf'")
    test_alpha_trace_logging_channels()
    test_beta_trace_logging_channels()
    test_gamma_trace_logging_channels()
    trace.trace("orchestrator", "omega completed imported SDK trace checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
