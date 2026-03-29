from __future__ import annotations

import contextlib
import io
import unittest

from _support import kcli


class InlineRootTests(unittest.TestCase):
    def test_inline_bare_root_prints_help(self) -> None:
        argv = ["prog", "--build"]
        parser = kcli.Parser()
        build = kcli.InlineParser("build")
        build.setHandler("-flag", lambda context: None, "Enable build flag.")
        build.setHandler("-value", lambda context, value: None, "Set build value.")
        parser.addInlineParser(build)

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            parser.parseOrExit(len(argv), argv)
        output = stream.getvalue()

        self.assertIn("Available --build-* options:", output)
        self.assertIn("--build-flag", output)
        self.assertIn("--build-value <value>", output)

    def test_inline_root_value_handler_help_row_prints(self) -> None:
        argv = ["prog", "--build"]
        parser = kcli.Parser()
        build = kcli.InlineParser("build")
        build.setRootValueHandler(lambda context, value: None, "<selector>", "Select build targets.")
        build.setHandler("-flag", lambda context: None, "Enable build flag.")
        parser.addInlineParser(build)

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            parser.parseOrExit(len(argv), argv)
        output = stream.getvalue()

        self.assertIn("--build <selector>", output)
        self.assertIn("Select build targets.", output)

    def test_inline_root_value_handler_joins_tokens(self) -> None:
        argv = ["prog", "--build", "fast", "mode"]
        received_value = ""
        received_tokens: list[str] = []
        received_option = ""

        parser = kcli.Parser()
        build = kcli.InlineParser("build")

        def on_root(context: kcli.HandlerContext, value: str) -> None:
            nonlocal received_value, received_tokens, received_option
            received_value = value
            received_tokens = list(context.value_tokens)
            received_option = context.option

        build.setRootValueHandler(on_root)
        parser.addInlineParser(build)

        parser.parseOrExit(len(argv), argv)
        self.assertEqual(received_value, "fast mode")
        self.assertEqual(received_tokens, ["fast", "mode"])
        self.assertEqual(received_option, "--build")

    def test_inline_missing_root_value_handler_errors(self) -> None:
        argv = ["prog", "--build", "fast"]
        parser = kcli.Parser()
        parser.addInlineParser(kcli.InlineParser("--build"))

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--build")
        self.assertIn("unknown value for option '--build'", str(raised.exception))

    def test_unknown_inline_option_errors(self) -> None:
        argv = ["prog", "--build-unknown"]
        parser = kcli.Parser()
        parser.addInlineParser(kcli.InlineParser("--build"))

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--build-unknown")
        self.assertIn("unknown option --build-unknown", str(raised.exception))

    def test_inline_parser_root_override_applies(self) -> None:
        argv = ["prog", "--newgamma-tag", "prod"]
        tag = ""

        parser = kcli.Parser()
        gamma = kcli.InlineParser("--gamma")

        def on_tag(context: kcli.HandlerContext, value: str) -> None:
            nonlocal tag
            tag = value

        gamma.setHandler("-tag", on_tag, "Set gamma tag.")
        gamma.setRoot("--newgamma")
        parser.addInlineParser(gamma)
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(tag, "prod")


if __name__ == "__main__":
    unittest.main()
