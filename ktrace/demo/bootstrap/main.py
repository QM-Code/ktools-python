#!/usr/bin/env python3

from __future__ import annotations

import sys

from pathlib import Path


def _configure_demo_imports() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = repo_root.parent

    for path in (
        repo_root / "src",
        workspace_root / "kcli" / "src",
    ):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


_configure_demo_imports()

import kcli
import ktrace


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)

    logger = ktrace.Logger()
    trace = ktrace.TraceLogger("bootstrap")
    trace.addChannel("app")
    logger.addTraceLogger(trace)
    logger.enableChannel(trace, ".app")

    parser = kcli.Parser()
    parser.addInlineParser(logger.makeInlineParser(trace))
    parser.parseOrExit(len(argv), argv)

    trace.trace("app", "ktrace python bootstrap passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
