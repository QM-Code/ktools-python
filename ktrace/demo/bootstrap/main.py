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

from sdk.common import ensure_workspace_paths

ensure_workspace_paths(__file__)

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
