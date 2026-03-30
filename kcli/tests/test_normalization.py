from __future__ import annotations

import unittest

from _support import kcli


class NormalizationTests(unittest.TestCase):
    def test_positional_handler_requires_nonempty(self) -> None:
        parser = kcli.Parser()
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            parser.set_positional_handler(None)  # type: ignore[arg-type]

    def test_end_user_handler_normalization_rejects_single_dash(self) -> None:
        parser = kcli.Parser()
        with self.assertRaisesRegex(ValueError, "end-user handler option must use '--name' or 'name'"):
            parser.set_handler("-verbose", lambda context: None, "Enable verbose logging.")

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

        build.set_handler("-flag", on_flag, "Enable build flag.")
        build.set_handler("--build-value", on_value, "Set build value.")
        parser.add_inline_parser(build)

        parser.parse_or_exit(argv)
        self.assertTrue(flag)
        self.assertEqual(value, "data")

    def test_inline_handler_normalization_rejects_wrong_root(self) -> None:
        parser = kcli.InlineParser("--build")
        with self.assertRaisesRegex(ValueError, "inline handler option must use '-name' or '--build-name'"):
            parser.set_handler("--other-flag", lambda context: None, "Enable other flag.")

    def test_duplicate_inline_root_rejected(self) -> None:
        parser = kcli.Parser()
        parser.add_inline_parser(kcli.InlineParser("--build"))
        with self.assertRaisesRegex(ValueError, "already registered"):
            parser.add_inline_parser(kcli.InlineParser("build"))


if __name__ == "__main__":
    unittest.main()
