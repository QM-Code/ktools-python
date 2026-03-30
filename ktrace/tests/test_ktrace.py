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
        trace.add_channel("net")
        trace.add_channel("cache")
        logger.add_trace_logger(trace)

        logger.enable_channels("tests.*")
        self.assertTrue(logger.is_channel_enabled("tests.net"))
        self.assertTrue(logger.is_channel_enabled("tests.cache"))

        logger.disable_channels("tests.*")
        self.assertFalse(logger.is_channel_enabled("tests.net"))
        self.assertFalse(logger.is_channel_enabled("tests.cache"))

        logger.enable_channel("tests.net")
        self.assertTrue(logger.is_channel_enabled("tests.net"))
        self.assertFalse(logger.is_channel_enabled("tests.cache"))

        logger.disable_channel("tests.net")
        self.assertFalse(logger.is_channel_enabled("tests.net"))

    def test_trace_disabled_by_default(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.add_channel("net")
        logger.add_trace_logger(trace)

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("net", "testing...")

        self.assertEqual(stream.getvalue(), "")

    def test_trace_emits_when_channel_enabled(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.add_channel("net")
        logger.add_trace_logger(trace)
        logger.enable_channels("alpha.net")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("net", "testing...")

        self.assertIn("[alpha] [net] testing...", stream.getvalue())

    def test_trace_changed_suppresses_duplicate_key(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("alpha")
        trace.add_channel("net")
        logger.add_trace_logger(trace)
        logger.enable_channels("alpha.net")

        def emit(key: str) -> None:
            trace.trace_changed("net", key, "changed")

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
        alpha.add_channel("net")
        alpha.add_channel("cache")
        beta = ktrace.TraceLogger("beta")
        beta.add_channel("io")
        beta.add_channel("scheduler")
        logger.add_trace_logger(alpha)
        logger.add_trace_logger(beta)
        logger.enable_channels("*.{net,io}")

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
        trace.add_channel("app")
        logger.add_trace_logger(trace)

        parser = kcli.Parser()
        parser.add_inline_parser(logger.build_inline_parser(trace))
        parser.parse_or_exit(["prog", "--trace", ".app"])

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("app", "testing...")

        self.assertIn("[core] [app] testing...", stream.getvalue())

    def test_make_inline_parser_honors_custom_root(self) -> None:
        import kcli

        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("core")
        trace.add_channel("app")
        logger.add_trace_logger(trace)

        parser = kcli.Parser()
        parser.add_inline_parser(logger.build_inline_parser(trace, "debug"))
        parser.parse_or_exit(["prog", "--debug", ".app"])

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            trace.trace("app", "testing...")

        self.assertIn("[core] [app] testing...", stream.getvalue())

    def test_make_inline_parser_examples_match_contract(self) -> None:
        import kcli

        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("core")
        trace.add_channel("app")
        logger.add_trace_logger(trace)

        parser = kcli.Parser()
        parser.add_inline_parser(logger.build_inline_parser(trace))

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            parser.parse_or_exit(["prog", "--trace-examples"])

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
        alpha.add_channel("net")
        beta = ktrace.TraceLogger("beta")
        beta.add_channel("io", ktrace.color("MediumSpringGreen"))
        logger.add_trace_logger(alpha)
        logger.add_trace_logger(beta)

        parser = kcli.Parser()
        parser.add_inline_parser(logger.build_inline_parser(alpha))

        namespace_stream = io.StringIO()
        with contextlib.redirect_stdout(namespace_stream):
            parser.parse_or_exit(["prog", "--trace-namespaces"])
        self.assertIn("  alpha", namespace_stream.getvalue())
        self.assertIn("  beta", namespace_stream.getvalue())

        channel_stream = io.StringIO()
        with contextlib.redirect_stdout(channel_stream):
            parser.parse_or_exit(["prog", "--trace-channels"])
        self.assertIn("  alpha.net", channel_stream.getvalue())
        self.assertIn("  beta.io", channel_stream.getvalue())

        color_stream = io.StringIO()
        with contextlib.redirect_stdout(color_stream):
            parser.parse_or_exit(["prog", "--trace-colors"])
        self.assertIn("  DeepSkyBlue1", color_stream.getvalue())
        self.assertIn("  MediumSpringGreen", color_stream.getvalue())

    def test_invalid_runtime_channel_queries_return_false(self) -> None:
        logger = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.add_channel("net")
        logger.add_trace_logger(trace)
        logger.enable_channels("tests.*")

        self.assertFalse(logger.is_channel_enabled("tests.bad name"))
        self.assertFalse(trace.is_channel_enabled("bad name"))

    def test_conflicting_explicit_channel_colors_are_rejected(self) -> None:
        logger = ktrace.Logger()

        first = ktrace.TraceLogger("tests")
        first.add_channel("net")
        logger.add_trace_logger(first)

        duplicate = ktrace.TraceLogger("tests")
        duplicate.add_channel("net")
        logger.add_trace_logger(duplicate)

        explicit_color = ktrace.TraceLogger("tests")
        explicit_color.add_channel("net", ktrace.color("Gold3"))
        logger.add_trace_logger(explicit_color)

        conflicting = ktrace.TraceLogger("tests")
        conflicting.add_channel("net", ktrace.color("Orange3"))

        with self.assertRaisesRegex(ValueError, "conflicting explicit channel colors"):
            logger.add_trace_logger(conflicting)

    def test_trace_logger_cannot_attach_to_multiple_loggers(self) -> None:
        first = ktrace.Logger()
        second = ktrace.Logger()
        trace = ktrace.TraceLogger("tests")
        trace.add_channel("net")

        first.add_trace_logger(trace)

        with self.assertRaisesRegex(ValueError, "already attached to another logger"):
            second.add_trace_logger(trace)

    def test_explicit_color_can_replace_default_color_registration(self) -> None:
        logger = ktrace.Logger()

        default_trace = ktrace.TraceLogger("tests")
        default_trace.add_channel("net")
        logger.add_trace_logger(default_trace)

        explicit_trace = ktrace.TraceLogger("tests")
        explicit_trace.add_channel("net", ktrace.color("Gold3"))
        logger.add_trace_logger(explicit_trace)

        logger.enable_channel("tests.net")

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
        logger.add_trace_logger(trace)
        logger.output_options = ktrace.OutputOptions(
            filenames=True,
            line_numbers=True,
            function_names=False,
            timestamps=False,
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
        trace.add_channel("changed")
        logger.add_trace_logger(trace)
        logger.enable_channel("tests.changed")

        stream = io.StringIO()

        def worker(thread_index: int) -> None:
            for iteration in range(500):
                trace.trace_changed("changed", f"{thread_index}:{iteration & 1}", "changed")

        with contextlib.redirect_stdout(stream):
            threads = [threading.Thread(target=worker, args=(index,)) for index in range(4)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertTrue(stream.getvalue())


if __name__ == "__main__":
    unittest.main()
