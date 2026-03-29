from __future__ import annotations

import subprocess
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_DEMO = REPO_ROOT / "demo" / "exe" / "core" / "main.py"


def run_demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(CORE_DEMO), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CoreCliTests(unittest.TestCase):
    def test_unknown_option(self) -> None:
        result = run_demo("--trace-f")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --trace-f", result.stderr)

    def test_blank_trace(self) -> None:
        result = run_demo("--trace")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --trace-* options:", result.stdout)
        self.assertIn("--trace <channels>", result.stdout)

    def test_timestamps_option(self) -> None:
        result = run_demo("--trace", ".app", "--trace-timestamps")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"\[core\] \[[0-9]+\.[0-9]{6}\] \[app\] cli processing enabled, use --trace for options",
        )

    def test_imported_selector(self) -> None:
        result = run_demo("--trace", "*.*")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[core] [app] cli processing enabled, use --trace for options", result.stdout)
        self.assertIn("testing imported tracing, use --trace '*.*' to view imported channels", result.stdout)
        self.assertIn("[alpha] [net] testing...", result.stdout)


if __name__ == "__main__":
    unittest.main()
