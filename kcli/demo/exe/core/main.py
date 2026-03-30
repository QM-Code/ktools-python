#!/usr/bin/env python3

from __future__ import annotations

import sys

from pathlib import Path

def _find_demo_root() -> Path:
    file_path = Path(__file__).resolve()
    for parent in file_path.parents:
        if (parent / "sdk").is_dir() and (parent / "tests").is_dir():
            return parent
    raise RuntimeError("unable to locate demo root")


DEMO_ROOT = _find_demo_root()
if str(DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEMO_ROOT))

def _ensure_repo_paths(current_file: str) -> None:
    file_path = Path(current_file).resolve()
    repo_root: Path | None = None
    for parent in file_path.parents:
        if (parent / "src").is_dir() and (parent / "demo").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError("unable to locate repository root for core demo")

    src_root = repo_root / "src"
    path = str(src_root)
    if path not in sys.path:
        sys.path.insert(0, path)


_ensure_repo_paths(__file__)

import kcli

from sdk.alpha import get_inline_parser


def _executable_name(path: str | None) -> str:
    if not path:
        return "app"
    return path


def _handle_verbose(context: kcli.HandlerContext) -> None:
    pass


def _handle_output(context: kcli.HandlerContext, value: str) -> None:
    pass


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    exe_name = _executable_name(argv[0] if argv else None)

    parser = kcli.Parser()
    parser.add_inline_parser(get_inline_parser())

    parser.add_alias("-v", "--verbose")
    parser.add_alias("-out", "--output")
    parser.add_alias("-a", "--alpha-enable")

    parser.set_handler("--verbose", _handle_verbose, "Enable verbose app logging.")
    parser.set_handler("--output", _handle_output, "Set app output target.")
    parser.parse_or_exit(argv)

    print("\nKCLI python demo core import/integration check passed\n")
    print("Usage:")
    print(f"  {exe_name} --alpha")
    print(f"  {exe_name} --output stdout\n")
    print("Enabled inline roots:")
    print("  --alpha\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
