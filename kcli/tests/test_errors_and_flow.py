from __future__ import annotations

import contextlib
import io
import unittest

from _support import kcli


class ErrorAndFlowTests(unittest.TestCase):
    def test_parser_empty_parse_succeeds(self) -> None:
        argv = ["prog"]
        parser = kcli.Parser()
        parser.parseOrExit(len(argv), argv)
        self.assertEqual(argv, ["prog"])

    def test_end_user_known_options_with_unknown_option_error(self) -> None:
        argv = ["prog", "--verbose", "pos1", "--output", "stdout", "--bogus", "pos2"]
        verbose = False
        output = ""
        positionals: list[str] = []

        parser = kcli.Parser()

        def on_verbose(context: kcli.HandlerContext) -> None:
            nonlocal verbose
            verbose = True

        def on_output(context: kcli.HandlerContext, value: str) -> None:
            nonlocal output
            output = value

        parser.setHandler("verbose", on_verbose, "Enable verbose logging.")
        parser.setHandler("output", on_output, "Set output target.")
        parser.setPositionalHandler(lambda context: positionals.extend(context.value_tokens))

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertFalse(verbose)
        self.assertEqual(output, "")
        self.assertEqual(positionals, [])
        self.assertEqual(raised.exception.option(), "--bogus")
        self.assertIn("unknown option --bogus", str(raised.exception))
        self.assertEqual(argv, ["prog", "--verbose", "pos1", "--output", "stdout", "--bogus", "pos2"])

    def test_parser_can_be_reused_across_parses(self) -> None:
        first = ["prog", "-v"]
        second = ["prog", "-v"]
        calls = 0

        parser = kcli.Parser()
        parser.addAlias("-v", "--verbose")

        def on_verbose(context: kcli.HandlerContext) -> None:
            nonlocal calls
            calls += 1

        parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")
        parser.parseOrExit(len(first), first)
        parser.parseOrExit(len(second), second)

        self.assertEqual(calls, 2)
        self.assertEqual(first, ["prog", "-v"])
        self.assertEqual(second, ["prog", "-v"])

    def test_unknown_option_reports_double_dash(self) -> None:
        argv = ["prog", "--"]
        parser = kcli.Parser()

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--")

    def test_unknown_option_throws_cli_error(self) -> None:
        argv = ["prog", "--bogus"]
        parser = kcli.Parser()

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--bogus")
        self.assertIn("unknown option --bogus", str(raised.exception))

    def test_option_handler_exception_throws_cli_error(self) -> None:
        argv = ["prog", "--verbose"]
        parser = kcli.Parser()

        def on_verbose(context: kcli.HandlerContext) -> None:
            raise RuntimeError("option boom")

        parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--verbose")
        self.assertIn("option boom", str(raised.exception))
        self.assertIn("--verbose", str(raised.exception))

    def test_positional_handler_exception_throws_cli_error(self) -> None:
        argv = ["prog", "tail"]
        parser = kcli.Parser()
        parser.setPositionalHandler(lambda context: (_ for _ in ()).throw(RuntimeError("positional boom")))

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "")
        self.assertIn("positional boom", str(raised.exception))

    def test_parse_or_exit_reports_and_exits(self) -> None:
        argv = ["prog", "--bogus"]
        parser = kcli.Parser()
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                parser.parseOrExit(len(argv), argv)

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("[error] [cli] unknown option --bogus", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
