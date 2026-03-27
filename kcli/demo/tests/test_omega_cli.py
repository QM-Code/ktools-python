from __future__ import annotations

import subprocess
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OMEGA_DEMO = REPO_ROOT / "demo" / "exe" / "omega" / "main.py"


def run_demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(OMEGA_DEMO), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class OmegaCliTests(unittest.TestCase):
    def test_unknown_alpha_option(self) -> None:
        result = run_demo("--alpha-d")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --alpha-d", result.stderr)

    def test_unknown_beta_option(self) -> None:
        result = run_demo("--beta-z")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --beta-z", result.stderr)

    def test_unknown_newgamma_option(self) -> None:
        result = run_demo("--newgamma-wut")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --newgamma-wut", result.stderr)

    def test_known_alpha_option(self) -> None:
        result = run_demo("--alpha-message", "hello")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with value "hello"', result.stdout)

    def test_alpha_multi_value(self) -> None:
        result = run_demo("--alpha-message", "hello", "world")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --alpha-message with values ["hello","world"]', result.stdout)

    def test_beta_workers_option(self) -> None:
        result = run_demo("--beta-workers", "8")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --beta-workers with value "8"', result.stdout)

    def test_beta_workers_invalid_option(self) -> None:
        result = run_demo("--beta-workers", "abc")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] option '--beta-workers': expected an integer", result.stderr)
        self.assertNotIn("Processing --beta-workers", result.stdout)

    def test_newgamma_tag_option(self) -> None:
        result = run_demo("--newgamma-tag", "prod")
        self.assertEqual(result.returncode, 0)
        self.assertIn('Processing --newgamma-tag with value "prod"', result.stdout)

    def test_alpha_help_root(self) -> None:
        result = run_demo("--alpha")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --alpha-* options:", result.stdout)
        self.assertIn("--alpha-enable [value]", result.stdout)

    def test_newgamma_help_root(self) -> None:
        result = run_demo("--newgamma")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --newgamma-* options:", result.stdout)
        self.assertIn("--newgamma-tag <value>", result.stdout)

    def test_unknown_app_option(self) -> None:
        result = run_demo("--bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --bogus", result.stderr)

    def test_known_and_unknown_option(self) -> None:
        result = run_demo("--alpha-message", "hello", "--bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --bogus", result.stderr)
        self.assertNotIn('Processing --alpha-message with value "hello"', result.stdout)

    def test_alpha_alias_option(self) -> None:
        result = run_demo("-a")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Processing --alpha-enable", result.stdout)

    def test_output_option(self) -> None:
        result = run_demo("--output", "stdout")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Enabled --<root> prefixes:", result.stdout)

    def test_output_alias_option(self) -> None:
        result = run_demo("-out", "stdout")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Enabled --<root> prefixes:", result.stdout)

    def test_build_profile_option(self) -> None:
        result = run_demo("--build-profile", "debug")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Enabled --<root> prefixes:", result.stdout)

    def test_build_alias_option(self) -> None:
        result = run_demo("-b", "debug")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Enabled --<root> prefixes:", result.stdout)

    def test_positional_args(self) -> None:
        result = run_demo("input-a", "input-b")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Enabled --<root> prefixes:", result.stdout)

    def test_double_dash_not_separator(self) -> None:
        result = run_demo("--", "--alpha-message", "hello")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --", result.stderr)
        self.assertNotIn('Processing --alpha-message with value "hello"', result.stdout)


if __name__ == "__main__":
    unittest.main()
