from __future__ import annotations

from .common import ensure_workspace_paths

ensure_workspace_paths(__file__)

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
