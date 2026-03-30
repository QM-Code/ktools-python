from __future__ import annotations

import subprocess
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_DEMO = REPO_ROOT / "demo" / "bootstrap" / "main.py"


def run_demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(BOOTSTRAP_DEMO), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class BootstrapCliTests(unittest.TestCase):
    def test_verbose_option(self) -> None:
        result = run_demo("--verbose")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Processing --verbose", result.stdout)
        self.assertIn("KCLI python bootstrap import/parse check passed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_verbose_alias_option(self) -> None:
        result = run_demo("-v")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Processing --verbose", result.stdout)
        self.assertIn("KCLI python bootstrap import/parse check passed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_unknown_option(self) -> None:
        result = run_demo("--bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --bogus", result.stderr)
        self.assertNotIn("KCLI python bootstrap import/parse check passed", result.stdout)

    def test_double_dash_not_separator(self) -> None:
        result = run_demo("--", "-v")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --", result.stderr)
        self.assertNotIn("Processing --verbose", result.stdout)


if __name__ == "__main__":
    unittest.main()
