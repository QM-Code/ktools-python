from __future__ import annotations

import subprocess
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_DEMO = REPO_ROOT / "demo" / "exe" / "core" / "main.py"


def run_demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CORE_DEMO), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CoreCliTests(unittest.TestCase):
    def test_unknown_alpha_option(self) -> None:
        result = run_demo("--alpha-d")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --alpha-d", result.stderr)
        self.assertNotIn("KCLI python demo core import/integration check passed", result.stdout)

    def test_known_alpha_option(self) -> None:
        result = run_demo("--alpha-message", "hello")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with value "hello"', result.stdout)
        self.assertNotIn("CLI error:", result.stdout + result.stderr)

    def test_alpha_multi_value(self) -> None:
        result = run_demo("--alpha-message", "hello", "world")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with values ["hello","world"]', result.stdout)

    def test_alpha_required_whitespace_value(self) -> None:
        result = run_demo("--alpha-message", " Joe ")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with value " Joe "', result.stdout)

    def test_alpha_optional_explicit_empty_value(self) -> None:
        result = run_demo("--alpha-enable", "")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-enable with value ""', result.stdout)

    def test_alpha_required_alias_like_value(self) -> None:
        result = run_demo("--alpha-message", "-a")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with value "-a"', result.stdout)
        self.assertNotIn("Processing --alpha-enable", result.stdout)

    def test_alpha_optional_no_value(self) -> None:
        result = run_demo("--alpha-enable")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Processing --alpha-enable", result.stdout)

    def test_alpha_alias_option(self) -> None:
        result = run_demo("-a")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Processing --alpha-enable", result.stdout)

    def test_alpha_help_root(self) -> None:
        result = run_demo("--alpha")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --alpha-* options:", result.stdout)
        self.assertIn("--alpha-enable [value]", result.stdout)

    def test_unknown_app_option(self) -> None:
        result = run_demo("--bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --bogus", result.stderr)
        self.assertNotIn("KCLI python demo core import/integration check passed", result.stdout)

    def test_output_option(self) -> None:
        result = run_demo("--output", "stdout")
        self.assertEqual(result.returncode, 0)
        self.assertIn("KCLI python demo core import/integration check passed", result.stdout)

    def test_output_alias_option(self) -> None:
        result = run_demo("-out", "stdout")
        self.assertEqual(result.returncode, 0)
        self.assertIn("KCLI python demo core import/integration check passed", result.stdout)

    def test_double_dash_not_separator(self) -> None:
        result = run_demo("--", "--alpha-message", "hello")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --", result.stderr)
        self.assertNotIn("KCLI python demo core import/integration check passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
