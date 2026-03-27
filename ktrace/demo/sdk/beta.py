from __future__ import annotations

from .common import ensure_workspace_paths

ensure_workspace_paths(__file__)

import ktrace


_TRACE_LOGGER: ktrace.TraceLogger | None = None


def get_trace_logger() -> ktrace.TraceLogger:
    global _TRACE_LOGGER
    if _TRACE_LOGGER is not None:
        return _TRACE_LOGGER

    trace = ktrace.TraceLogger("beta")
    trace.addChannel("io", ktrace.Color("MediumSpringGreen"))
    trace.addChannel("scheduler", ktrace.Color("Orange3"))
    _TRACE_LOGGER = trace
    return _TRACE_LOGGER


def test_trace_logging_channels() -> None:
    trace = get_trace_logger()
    trace.trace("io", "beta trace test on channel 'io'")
    trace.trace("scheduler", "beta trace test on channel 'scheduler'")
