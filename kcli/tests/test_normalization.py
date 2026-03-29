from __future__ import annotations

import unittest

from _support import kcli


class NormalizationTests(unittest.TestCase):
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

    def test_duplicate_inline_root_rejected(self) -> None:
        parser = kcli.Parser()
        parser.addInlineParser(kcli.InlineParser("--build"))
        with self.assertRaisesRegex(ValueError, "already registered"):
            parser.addInlineParser(kcli.InlineParser("build"))


if __name__ == "__main__":
    unittest.main()
