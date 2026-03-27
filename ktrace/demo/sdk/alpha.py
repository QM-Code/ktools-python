from __future__ import annotations

from .common import ensure_workspace_paths

ensure_workspace_paths(__file__)

import ktrace


_TRACE_LOGGER: ktrace.TraceLogger | None = None


def get_trace_logger() -> ktrace.TraceLogger:
    global _TRACE_LOGGER
    if _TRACE_LOGGER is not None:
        return _TRACE_LOGGER

    trace = ktrace.TraceLogger("alpha")
    trace.addChannel("net", ktrace.Color("DeepSkyBlue1"))
    trace.addChannel("net.alpha")
    trace.addChannel("net.beta")
    trace.addChannel("net.gamma")
    trace.addChannel("net.gamma.deep")
    trace.addChannel("cache", ktrace.Color("Gold3"))
    trace.addChannel("cache.gamma", ktrace.Color("Gold3"))
    trace.addChannel("cache.delta")
    trace.addChannel("cache.special", ktrace.Color("Red"))
    _TRACE_LOGGER = trace
    return _TRACE_LOGGER


def test_trace_logging_channels() -> None:
    trace = get_trace_logger()
    trace.trace("net", "testing...")
    trace.trace("net.alpha", "testing...")
    trace.trace("net.beta", "testing...")
    trace.trace("net.gamma", "testing...")
    trace.trace("net.gamma.deep", "testing...")
    trace.trace("cache", "testing...")
    trace.trace("cache.gamma", "testing...")
    trace.trace("cache.delta", "testing...")
    trace.trace("cache.special", "testing...")
