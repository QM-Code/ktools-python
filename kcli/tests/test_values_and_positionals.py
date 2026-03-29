from __future__ import annotations

import unittest

from _support import kcli


class ValuesAndPositionalsTests(unittest.TestCase):
    def test_optional_value_handler_allows_missing_value(self) -> None:
        argv = ["prog", "--build-enable"]
        called = False
        received_value = None
        received_tokens: list[str] = []

        parser = kcli.Parser()
        build = kcli.InlineParser("build")

        def on_enable(context: kcli.HandlerContext, value: str) -> None:
            nonlocal called, received_value, received_tokens
            called = True
            received_value = value
            received_tokens = list(context.value_tokens)

        build.setOptionalValueHandler("-enable", on_enable, "Enable build mode.")
        parser.addInlineParser(build)
        parser.parseOrExit(len(argv), argv)

        self.assertTrue(called)
        self.assertEqual(received_value, "")
        self.assertEqual(received_tokens, [])

    def test_optional_value_handler_accepts_explicit_empty_value(self) -> None:
        argv = ["prog", "--build-enable", ""]
        received_value = None
        received_tokens: list[str] = []

        parser = kcli.Parser()
        build = kcli.InlineParser("build")

        def on_enable(context: kcli.HandlerContext, value: str) -> None:
            nonlocal received_value, received_tokens
            received_value = value
            received_tokens = list(context.value_tokens)

        build.setOptionalValueHandler("-enable", on_enable, "Enable build mode.")
        parser.addInlineParser(build)
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(received_value, "")
        self.assertEqual(received_tokens, [""])

    def test_flag_handler_does_not_consume_following_tokens(self) -> None:
        argv = ["prog", "--build-meta", "data"]
        called = False
        positionals: list[str] = []

        parser = kcli.Parser()
        build = kcli.InlineParser("build")

        def on_meta(context: kcli.HandlerContext) -> None:
            nonlocal called
            called = True

        build.setHandler("-meta", on_meta, "Record metadata.")
        parser.addInlineParser(build)
        parser.setPositionalHandler(lambda context: positionals.extend(context.value_tokens))
        parser.parseOrExit(len(argv), argv)

        self.assertTrue(called)
        self.assertEqual(positionals, ["data"])

    def test_required_value_handler_rejects_missing_value(self) -> None:
        argv = ["prog", "--build-value"]
        parser = kcli.Parser()
        build = kcli.InlineParser("build")
        build.setHandler("-value", lambda context, value: None, "Set build value.")
        parser.addInlineParser(build)

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--build-value")
        self.assertIn("requires a value", str(raised.exception))

    def test_required_value_handler_accepts_dash_prefixed_first_value(self) -> None:
        argv = ["prog", "--build-value", "-debug"]
        value = ""

        def on_value(context: kcli.HandlerContext, raw_value: str) -> None:
            nonlocal value
            value = raw_value

        build = kcli.InlineParser("build")
        build.setHandler("-value", on_value, "Set build value.")
        parser = kcli.Parser()
        parser.addInlineParser(build)
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(value, "-debug")

    def test_required_value_handler_preserves_shell_whitespace(self) -> None:
        argv = ["prog", "--name", " Joe "]
        received_value = ""
        received_tokens: list[str] = []

        parser = kcli.Parser()

        def on_name(context: kcli.HandlerContext, value: str) -> None:
            nonlocal received_value, received_tokens
            received_value = value
            received_tokens = list(context.value_tokens)

        parser.setHandler("--name", on_name, "Set the display name.")
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(received_value, " Joe ")
        self.assertEqual(received_tokens, [" Joe "])

    def test_required_value_handler_accepts_explicit_empty_value(self) -> None:
        argv = ["prog", "--name", ""]
        received_value = "sentinel"
        received_tokens: list[str] = []

        parser = kcli.Parser()

        def on_name(context: kcli.HandlerContext, value: str) -> None:
            nonlocal received_value, received_tokens
            received_value = value
            received_tokens = list(context.value_tokens)

        parser.setHandler("--name", on_name, "Set the display name.")
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(received_value, "")
        self.assertEqual(received_tokens, [""])

    def test_positional_handler_preserves_explicit_empty_tokens(self) -> None:
        argv = ["prog", "", "tail"]
        positionals: list[str] = []

        parser = kcli.Parser()
        parser.setPositionalHandler(lambda context: positionals.extend(context.value_tokens))
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(positionals, ["", "tail"])

    def test_single_pass_processing_consumes_inline_end_user_and_positionals(self) -> None:
        argv = ["prog", "tail", "--alpha-message", "hello", "--output", "stdout"]
        alpha_message = ""
        output = ""
        positionals: list[str] = []

        parser = kcli.Parser()
        alpha = kcli.InlineParser("alpha")

        def on_message(context: kcli.HandlerContext, value: str) -> None:
            nonlocal alpha_message
            alpha_message = value

        def on_output(context: kcli.HandlerContext, value: str) -> None:
            nonlocal output
            output = value

        alpha.setHandler("-message", on_message, "Set alpha message.")
        parser.addInlineParser(alpha)
        parser.setHandler("--output", on_output, "Set output target.")
        parser.setPositionalHandler(lambda context: positionals.extend(context.value_tokens))
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(alpha_message, "hello")
        self.assertEqual(output, "stdout")
        self.assertEqual(positionals, ["tail"])


if __name__ == "__main__":
    unittest.main()
