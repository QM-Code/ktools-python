from __future__ import annotations

import contextlib
import io
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = REPO_ROOT / "src"
KCLI_PYTHON_ROOT = REPO_ROOT.parent / "kcli" / "src"

for path in (str(PYTHON_ROOT), str(KCLI_PYTHON_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import ktrace


class KtraceTests(unittest.TestCase):
    def test_trace_disabled_by_default(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.addChannel("net")
        logger.addTraceLogger(trace)

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("net", "testing...")

        self.assertEqual(stream.getvalue(), "")

    def test_trace_emits_when_channel_enabled(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.addChannel("net")
        logger.addTraceLogger(trace)
        logger.enableChannels("alpha.net")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("net", "testing...")

        self.assertIn("[alpha] [net] testing...", stream.getvalue())

    def test_trace_changed_suppresses_duplicate_key(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.addChannel("net")
        logger.addTraceLogger(trace)
        logger.enableChannels("alpha.net")

        def emit(key: str) -> None:
            trace.traceChanged("net", key, "changed")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            emit("same")
            emit("same")
            emit("next")

        lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 2)

    def test_brace_selector_matches_subset(self) -> None:
        logger = ktrace.Logger()
        alpha = ktrace.TraceLogger("alpha")
        alpha.addChannel("net")
        alpha.addChannel("cache")
        beta = ktrace.TraceLogger("beta")
        beta.addChannel("io")
        beta.addChannel("scheduler")
        logger.addTraceLogger(alpha)
        logger.addTraceLogger(beta)
        logger.enableChannels("*.{net,io}")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            alpha.trace("net", "alpha net")
            alpha.trace("cache", "alpha cache")
            beta.trace("io", "beta io")
            beta.trace("scheduler", "beta scheduler")

        output = stream.getvalue()
        self.assertIn("alpha net", output)
        self.assertIn("beta io", output)
        self.assertNotIn("alpha cache", output)
        self.assertNotIn("beta scheduler", output)

    def test_make_inline_parser_enables_local_channel(self) -> None:
        import kcli

        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("core")
        trace.addChannel("app")
        logger.addTraceLogger(trace)

        parser = kcli.Parser()
        parser.addInlineParser(logger.makeInlineParser(trace))
        parser.parseOrExit(3, ["prog", "--trace", ".app"])

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("app", "testing...")

        self.assertIn("[core] [app] testing...", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
