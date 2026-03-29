from __future__ import annotations

import subprocess
import sys
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OMEGA_DEMO = REPO_ROOT / "demo" / "exe" / "omega" / "main.py"


def run_demo(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(OMEGA_DEMO), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class OmegaCliTests(unittest.TestCase):
    def test_unknown_option(self) -> None:
        result = run_demo("--trace-f")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --trace-f", result.stderr)

    def test_blank_trace(self) -> None:
        result = run_demo("--trace")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Available --trace-* options:", result.stdout)
        self.assertIn("--trace <channels>", result.stdout)

    def test_bad_selector(self) -> None:
        result = run_demo("--trace", "*")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] option '--trace': Invalid trace selector: '*' (did you mean '.*'?)", result.stderr)

    def test_exact_selector_warning(self) -> None:
        result = run_demo("--trace", ".missing")
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "[omega] [warning] enable ignored channel selector 'omega.missing' because it matched no registered channels",
            result.stdout,
        )

    def test_wildcard_selector_warning(self) -> None:
        result = run_demo("--trace", "missing.*")
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "[omega] [warning] enable ignored channel selector 'missing.*' because it matched no registered channels",
            result.stdout,
        )

    def test_timestamps_option(self) -> None:
        result = run_demo("--trace", ".app", "--trace-timestamps")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"\[omega\] \[[0-9]+\.[0-9]{6}\] \[app\] cli processing enabled, use --trace for options",
        )
        self.assertRegex(
            result.stdout,
            r"\[omega\] \[[0-9]+\.[0-9]{6}\] \[app\] testing external tracing, use --trace '\*\.\*' to view top-level channels",
        )

    def test_files_option(self) -> None:
        result = run_demo("--trace", ".app", "--trace-files")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"\[omega\] \[app\] \[main:[0-9]+\] cli processing enabled, use --trace for options",
        )

    def test_functions_option(self) -> None:
        result = run_demo("--trace", ".app", "--trace-functions")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"\[omega\] \[app\] \[main:[0-9]+:main\] cli processing enabled, use --trace for options",
        )

    def test_functions_with_timestamps_option(self) -> None:
        result = run_demo("--trace", ".app", "--trace-timestamps", "--trace-functions")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"\[omega\] \[[0-9]+\.[0-9]{6}\] \[app\] \[main:[0-9]+:main\] cli processing enabled, use --trace for options",
        )
        self.assertNotIn("CLI error:", result.stdout)

    def test_removed_lines_option_is_unknown(self) -> None:
        result = run_demo("--trace", ".app", "--trace-lines")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[error] [cli] unknown option --trace-lines", result.stderr)
        self.assertNotIn("Trace selector examples:", result.stderr)

    def test_wildcard_all_depth3(self) -> None:
        result = run_demo("--trace", "*.*.*.*")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[omega] [app] omega initialized local trace channels", result.stdout)
        self.assertIn("omega trace test on channel 'deep.branch.leaf'", result.stdout)
        self.assertIn("[alpha] [net] testing...", result.stdout)
        self.assertIn("beta trace test on channel 'io'", result.stdout)
        self.assertIn("gamma trace test on channel 'physics'", result.stdout)

    def test_brace_selector(self) -> None:
        result = run_demo("--trace", "*.{net,io}")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[alpha] [net] testing...", result.stdout)
        self.assertIn("beta trace test on channel 'io'", result.stdout)
        self.assertNotIn("[alpha] [cache] testing...", result.stdout)
        self.assertNotIn("beta trace test on channel 'scheduler'", result.stdout)
        self.assertNotIn("gamma trace test on channel 'physics'", result.stdout)


if __name__ == "__main__":
    unittest.main()
