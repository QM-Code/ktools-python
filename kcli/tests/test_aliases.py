from __future__ import annotations

import unittest

from _support import kcli


class AliasTests(unittest.TestCase):
    def test_add_alias_rewrites_tokens(self) -> None:
        argv = ["prog", "-v", "tail"]
        seen_option = ""

        parser = kcli.Parser()
        parser.addAlias("-v", "--verbose")

        def on_verbose(context: kcli.HandlerContext) -> None:
            nonlocal seen_option
            seen_option = context.option

        parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(seen_option, "--verbose")
        self.assertEqual(argv, ["prog", "-v", "tail"])

    def test_add_alias_preset_tokens_append_to_value_handlers(self) -> None:
        argv = ["prog", "-c", "settings.json"]
        option = ""
        value = ""
        tokens: list[str] = []

        parser = kcli.Parser()
        parser.addAlias("-c", "--config-load", ["user-file"])

        def on_load(context: kcli.HandlerContext, captured: str) -> None:
            nonlocal option, value, tokens
            option = context.option
            value = captured
            tokens = list(context.value_tokens)

        parser.setHandler("--config-load", on_load, "Load config.")
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(option, "--config-load")
        self.assertEqual(value, "user-file settings.json")
        self.assertEqual(tokens, ["user-file", "settings.json"])
        self.assertEqual(argv, ["prog", "-c", "settings.json"])

    def test_add_alias_preset_tokens_satisfy_required_values(self) -> None:
        argv = ["prog", "-p"]
        value = ""
        tokens: list[str] = []

        parser = kcli.Parser()
        parser.addAlias("-p", "--profile", ["release"])

        def on_profile(context: kcli.HandlerContext, captured: str) -> None:
            nonlocal value, tokens
            self.assertEqual(context.option, "--profile")
            value = captured
            tokens = list(context.value_tokens)

        parser.setHandler("--profile", on_profile, "Set the active profile.")
        parser.parseOrExit(len(argv), argv)

        self.assertEqual(value, "release")
        self.assertEqual(tokens, ["release"])
        self.assertEqual(argv, ["prog", "-p"])

    def test_add_alias_preset_tokens_apply_to_inline_root_values(self) -> None:
        argv = ["prog", "-c"]
        handled = False
        value = ""
        tokens: list[str] = []

        parser = kcli.Parser()
        config = kcli.InlineParser("--config")

        def on_root(context: kcli.HandlerContext, captured: str) -> None:
            nonlocal handled, value, tokens
            handled = True
            self.assertEqual(context.option, "--config")
            value = captured
            tokens = list(context.value_tokens)

        config.setRootValueHandler(on_root, "<assignment>", "Store a config assignment.")
        parser.addInlineParser(config)
        parser.addAlias("-c", "--config", ["user-file=/tmp/user.json"])

        parser.parseOrExit(len(argv), argv)

        self.assertTrue(handled)
        self.assertEqual(value, "user-file=/tmp/user.json")
        self.assertEqual(tokens, ["user-file=/tmp/user.json"])
        self.assertEqual(argv, ["prog", "-c"])

    def test_add_alias_rewrites_after_double_dash(self) -> None:
        argv = ["prog", "--", "-v"]
        parser = kcli.Parser()
        parser.addAlias("-v", "--verbose")
        parser.setHandler("--verbose", lambda context: None, "Enable verbose logging.")

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--")
        self.assertEqual(argv, ["prog", "--", "-v"])

    def test_alias_does_not_rewrite_required_value_tokens(self) -> None:
        argv = ["prog", "--output", "-v"]
        verbose = False
        output = ""

        parser = kcli.Parser()
        parser.addAlias("-v", "--verbose")

        def on_verbose(context: kcli.HandlerContext) -> None:
            nonlocal verbose
            verbose = True

        def on_output(context: kcli.HandlerContext, value: str) -> None:
            nonlocal output
            output = value

        parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")
        parser.setHandler("--output", on_output, "Set output target.")
        parser.parseOrExit(len(argv), argv)

        self.assertFalse(verbose)
        self.assertEqual(output, "-v")
        self.assertEqual(argv, ["prog", "--output", "-v"])

    def test_alias_rejects_invalid_configurations(self) -> None:
        parser = kcli.Parser()
        with self.assertRaisesRegex(ValueError, "single-dash form"):
            parser.addAlias("--verbose", "--output")
        with self.assertRaisesRegex(ValueError, "double-dash form"):
            parser.addAlias("-v", "--bad target")
        with self.assertRaisesRegex(ValueError, "double-dash form"):
            parser.addAlias("-a", "-b")

    def test_add_alias_rejects_preset_values_for_flag_targets(self) -> None:
        argv = ["prog", "-v"]
        parser = kcli.Parser()
        parser.addAlias("-v", "--verbose", ["unexpected"])
        parser.setHandler("--verbose", lambda context: None, "Enable verbose logging.")

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "-v")
        self.assertIn("does not accept values", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
