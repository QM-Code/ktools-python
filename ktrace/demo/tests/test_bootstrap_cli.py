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
    def test_blank_trace(self) -> None:
        result = run_demo("--trace")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --trace-* options:", result.stdout)
        self.assertIn("--trace <channels>", result.stdout)

    def test_local_selector_enables_bootstrap_trace(self) -> None:
        result = run_demo("--trace", ".app")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[bootstrap] [app] ktrace python bootstrap passed", result.stdout)

    def test_examples_output_includes_brace_selector_examples(self) -> None:
        result = run_demo("--trace-examples")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--trace '*.{net,io}'", result.stdout)
        self.assertIn("--trace '{alpha,beta}.net'", result.stdout)


if __name__ == "__main__":
    unittest.main()
