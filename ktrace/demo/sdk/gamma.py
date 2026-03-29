from __future__ import annotations

import sys

from pathlib import Path


def _configure_demo_imports() -> None:
    repo_root = Path(__file__).resolve().parents[2]
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

import ktrace


_TRACE_LOGGER: ktrace.TraceLogger | None = None


def get_trace_logger() -> ktrace.TraceLogger:
    global _TRACE_LOGGER
    if _TRACE_LOGGER is not None:
        return _TRACE_LOGGER

    trace = ktrace.TraceLogger("gamma")
    trace.addChannel("physics", ktrace.Color("MediumOrchid1"))
    trace.addChannel("metrics", ktrace.Color("LightSkyBlue1"))
    _TRACE_LOGGER = trace
    return _TRACE_LOGGER


def test_trace_logging_channels() -> None:
    trace = get_trace_logger()
    trace.trace("physics", "gamma trace test on channel 'physics'")
    trace.trace("metrics", "gamma trace test on channel 'metrics'")
