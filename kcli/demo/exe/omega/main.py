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
        raise RuntimeError("unable to locate repository root for omega demo")

    src_root = repo_root / "src"
    path = str(src_root)
    if path not in sys.path:
        sys.path.insert(0, path)


_ensure_repo_paths(__file__)

import kcli

from sdk.alpha import get_inline_parser as get_alpha_inline_parser
from sdk.beta import get_inline_parser as get_beta_inline_parser
from sdk.gamma import get_inline_parser as get_gamma_inline_parser


def _handle_build_profile(context: kcli.HandlerContext, value: str) -> None:
    pass


def _handle_build_clean(context: kcli.HandlerContext) -> None:
    pass


def _handle_verbose(context: kcli.HandlerContext) -> None:
    pass


def _handle_output(context: kcli.HandlerContext, value: str) -> None:
    pass


def _handle_args(context: kcli.HandlerContext) -> None:
    pass


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)

    parser = kcli.Parser()
    alpha_parser = get_alpha_inline_parser()
    beta_parser = get_beta_inline_parser()
    gamma_parser = get_gamma_inline_parser()
    gamma_parser.setRoot("--newgamma")

    build_parser = kcli.InlineParser("--build")
    build_parser.setHandler("-profile", _handle_build_profile, "Set build profile.")
    build_parser.setHandler("-clean", _handle_build_clean, "Enable clean build.")

    parser.addInlineParser(alpha_parser)
    parser.addInlineParser(beta_parser)
    parser.addInlineParser(gamma_parser)
    parser.addInlineParser(build_parser)

    parser.addAlias("-v", "--verbose")
    parser.addAlias("-out", "--output")
    parser.addAlias("-a", "--alpha-enable")
    parser.addAlias("-b", "--build-profile")

    parser.setHandler("--verbose", _handle_verbose, "Enable verbose app logging.")
    parser.setHandler("--output", _handle_output, "Set app output target.")
    parser.setPositionalHandler(_handle_args)

    parser.parseOrExit(len(argv), argv)

    print("\nUsage:")
    print("  kcli_demo_omega --<root>\n")
    print("Enabled --<root> prefixes:")
    print("  --alpha")
    print("  --beta")
    print("  --newgamma (gamma override)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
