from __future__ import annotations

import contextlib
import io
import sys
import unittest

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = REPO_ROOT / "src"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

import kcli


class KcliTests(unittest.TestCase):
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

    def test_positional_handler_requires_nonempty(self) -> None:
        parser = kcli.Parser()
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            parser.setPositionalHandler(None)  # type: ignore[arg-type]

    def test_end_user_handler_normalization_rejects_single_dash(self) -> None:
        parser = kcli.Parser()
        with self.assertRaisesRegex(ValueError, "end-user handler option must use '--name' or 'name'"):
            parser.setHandler("-verbose", lambda context: None, "Enable verbose logging.")

    def test_inline_handler_normalization_accepts_short_and_full_forms(self) -> None:
        argv = ["prog", "--build-flag", "--build-value", "data"]
        flag = False
        value = ""

        parser = kcli.Parser()
        build = kcli.InlineParser("build")

        def on_flag(context: kcli.HandlerContext) -> None:
            nonlocal flag
            flag = True

        def on_value(context: kcli.HandlerContext, raw_value: str) -> None:
            nonlocal value
            value = raw_value

        build.setHandler("-flag", on_flag, "Enable build flag.")
        build.setHandler("--build-value", on_value, "Set build value.")
        parser.addInlineParser(build)

        parser.parseOrExit(len(argv), argv)
        self.assertTrue(flag)
        self.assertEqual(value, "data")

    def test_inline_handler_normalization_rejects_wrong_root(self) -> None:
        parser = kcli.InlineParser("--build")
        with self.assertRaisesRegex(ValueError, "inline handler option must use '-name' or '--build-name'"):
            parser.setHandler("--other-flag", lambda context: None, "Enable other flag.")

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

    def test_unknown_inline_option_errors(self) -> None:
        argv = ["prog", "--build-unknown"]
        parser = kcli.Parser()
        parser.addInlineParser(kcli.InlineParser("--build"))

        with self.assertRaises(kcli.CliError) as raised:
            parser.parseOrThrow(len(argv), argv)

        self.assertEqual(raised.exception.option(), "--build-unknown")
        self.assertIn("unknown option --build-unknown", str(raised.exception))

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

    def test_duplicate_inline_root_rejected(self) -> None:
        parser = kcli.Parser()
        parser.addInlineParser(kcli.InlineParser("--build"))
        with self.assertRaisesRegex(ValueError, "already registered"):
            parser.addInlineParser(kcli.InlineParser("build"))

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
