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
from sdk.beta import get_trace_logger as get_beta_trace_logger
from sdk.beta import test_trace_logging_channels as test_beta_trace_logging_channels
from sdk.gamma import get_trace_logger as get_gamma_trace_logger
from sdk.gamma import test_trace_logging_channels as test_gamma_trace_logging_channels


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)

    logger = ktrace.Logger()

    trace = ktrace.TraceLogger("omega")
    trace.add_channel("app", ktrace.color("BrightCyan"))
    trace.add_channel("orchestrator", ktrace.color("BrightYellow"))
    trace.add_channel("deep")
    trace.add_channel("deep.branch")
    trace.add_channel("deep.branch.leaf", ktrace.color("LightSalmon1"))

    logger.add_trace_logger(trace)
    logger.add_trace_logger(get_alpha_trace_logger())
    logger.add_trace_logger(get_beta_trace_logger())
    logger.add_trace_logger(get_gamma_trace_logger())

    logger.enable_channel(trace, ".app")
    trace.trace("app", "omega initialized local trace channels")
    logger.disable_channel(trace, ".app")

    parser = kcli.Parser()
    parser.add_inline_parser(logger.build_inline_parser(trace))
    parser.parse_or_exit(argv)

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
