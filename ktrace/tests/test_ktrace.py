from __future__ import annotations

import contextlib
import io
import sys
import threading
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
    def test_explicit_enable_disable_semantics(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.addChannel("net")
        trace.addChannel("cache")
        logger.addTraceLogger(trace)

        logger.enableChannels("tests.*")
        self.assertTrue(logger.shouldTraceChannel("tests.net"))
        self.assertTrue(logger.shouldTraceChannel("tests.cache"))

        logger.disableChannels("tests.*")
        self.assertFalse(logger.shouldTraceChannel("tests.net"))
        self.assertFalse(logger.shouldTraceChannel("tests.cache"))

        logger.enableChannel("tests.net")
        self.assertTrue(logger.shouldTraceChannel("tests.net"))
        self.assertFalse(logger.shouldTraceChannel("tests.cache"))

        logger.disableChannel("tests.net")
        self.assertFalse(logger.shouldTraceChannel("tests.net"))

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

    def test_make_inline_parser_honors_custom_root(self) -> None:
        import kcli

        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("core")
        trace.addChannel("app")
        logger.addTraceLogger(trace)

        parser = kcli.Parser()
        parser.addInlineParser(logger.makeInlineParser(trace, "debug"))
        parser.parseOrExit(3, ["prog", "--debug", ".app"])

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("app", "testing...")

        self.assertIn("[core] [app] testing...", stream.getvalue())

    def test_make_inline_parser_examples_match_contract(self) -> None:
        import kcli

        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("core")
        trace.addChannel("app")
        logger.addTraceLogger(trace)

        parser = kcli.Parser()
        parser.addInlineParser(logger.makeInlineParser(trace))

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            parser.parseOrExit(2, ["prog", "--trace-examples"])

        text = stream.getvalue()
        self.assertIn("General trace selector pattern:", text)
        self.assertIn("--trace '*.scheduler.tick'", text)
        self.assertIn("--trace '{alpha,beta}.*'", text)
        self.assertIn("--trace beta.{io,scheduler}.packet", text)
        self.assertIn("--trace '{alpha,beta}.net'", text)

    def test_make_inline_parser_lists_namespaces_channels_and_colors(self) -> None:
        import kcli

        logger = ktrace.Logger()
        alpha = ktrace.TraceLogger("alpha")
        alpha.addChannel("net")
        beta = ktrace.TraceLogger("beta")
        beta.addChannel("io", ktrace.Color("MediumSpringGreen"))
        logger.addTraceLogger(alpha)
        logger.addTraceLogger(beta)

        parser = kcli.Parser()
        parser.addInlineParser(logger.makeInlineParser(alpha))

        namespace_stream = io.StringIO()
        with contextlib.redirect_stdout(namespace_stream):
            parser.parseOrExit(2, ["prog", "--trace-namespaces"])
        self.assertIn("  alpha", namespace_stream.getvalue())
        self.assertIn("  beta", namespace_stream.getvalue())

        channel_stream = io.StringIO()
        with contextlib.redirect_stdout(channel_stream):
            parser.parseOrExit(2, ["prog", "--trace-channels"])
        self.assertIn("  alpha.net", channel_stream.getvalue())
        self.assertIn("  beta.io", channel_stream.getvalue())

        color_stream = io.StringIO()
        with contextlib.redirect_stdout(color_stream):
            parser.parseOrExit(2, ["prog", "--trace-colors"])
        self.assertIn("  DeepSkyBlue1", color_stream.getvalue())
        self.assertIn("  MediumSpringGreen", color_stream.getvalue())

    def test_invalid_runtime_channel_queries_return_false(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.addChannel("net")
        logger.addTraceLogger(trace)
        logger.enableChannels("tests.*")

        self.assertFalse(logger.shouldTraceChannel("tests.bad name"))
        self.assertFalse(trace.shouldTraceChannel("bad name"))

    def test_conflicting_explicit_channel_colors_are_rejected(self) -> None:
        logger = ktrace.Logger()

        first = ktrace.TraceLogger("tests")
        first.addChannel("net")
        logger.addTraceLogger(first)

        duplicate = ktrace.TraceLogger("tests")
        duplicate.addChannel("net")
        logger.addTraceLogger(duplicate)

        explicit_color = ktrace.TraceLogger("tests")
        explicit_color.addChannel("net", ktrace.Color("Gold3"))
        logger.addTraceLogger(explicit_color)

        conflicting = ktrace.TraceLogger("tests")
        conflicting.addChannel("net", ktrace.Color("Orange3"))

        with self.assertRaisesRegex(ValueError, "conflicting explicit channel colors"):
            logger.addTraceLogger(conflicting)

    def test_trace_logger_cannot_attach_to_multiple_loggers(self) -> None:
        first = ktrace.Logger()
        second = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.addChannel("net")

        first.addTraceLogger(trace)

        with self.assertRaisesRegex(ValueError, "already attached to another logger"):
            second.addTraceLogger(trace)

    def test_explicit_color_can_replace_default_color_registration(self) -> None:
        logger = ktrace.Logger()

        default_trace = ktrace.TraceLogger("tests")
        default_trace.addChannel("net")
        logger.addTraceLogger(default_trace)

        explicit_trace = ktrace.TraceLogger("tests")
        explicit_trace.addChannel("net", ktrace.Color("Gold3"))
        logger.addTraceLogger(explicit_trace)

        logger.enableChannel("tests.net")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            explicit_trace.trace("net", "testing...")

        self.assertIn("[tests] [net] testing...", stream.getvalue())

    def test_format_message_matches_public_contract(self) -> None:
        self.assertEqual(ktrace._api.format_message("value {} {}", 7, "done"), "value 7 done")
        self.assertEqual(ktrace._api.format_message("escaped {{}}"), "escaped {}")
        self.assertEqual(ktrace._api.format_message("bool {}", True), "bool true")

        for invalid_format in ("value {} {}", "value", "{", "}", "{:x}"):
            with self.subTest(invalid_format=invalid_format):
                with self.assertRaises(ValueError):
                    ktrace._api.format_message(invalid_format, 7)

    def test_public_log_output_respects_output_options(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        logger.addTraceLogger(trace)
        logger.setOutputOptions(
            ktrace.OutputOptions(
                filenames=True,
                line_numbers=True,
                function_names=False,
                timestamps=False,
            )
        )

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.info("info message")
            trace.warn("warn value {}", 7)
            trace.error("error message")

        text = stream.getvalue()
        self.assertTrue(text.startswith("[tests] [info] "))
        self.assertIn("\n[tests] [warning] ", text)
        self.assertIn("\n[tests] [error] ", text)
        self.assertIn("info message", text)
        self.assertIn("warn value 7", text)
        self.assertIn("error message", text)
        self.assertIn("test_ktrace:", text)
        self.assertNotIn("[info] [tests] [info]", text)
        self.assertNotIn("[warning] [tests] [warning]", text)
        self.assertNotIn("[error] [tests] [error]", text)

    def test_trace_changed_is_thread_safe_under_basic_contention(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.addChannel("changed")
        logger.addTraceLogger(trace)
        logger.enableChannel("tests.changed")

        stream = io.StringIO()

        def worker(thread_index: int) -> None:
            for iteration in range(500):
                trace.traceChanged("changed", f"{thread_index}:{iteration & 1}", "changed")

        with contextlib.redirect_stdout(stream):
            threads = [threading.Thread(target=worker, args=(index,)) for index in range(4)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertTrue(stream.getvalue())


if __name__ == "__main__":
    unittest.main()
