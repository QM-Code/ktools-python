from __future__ import annotations

import sys

from pathlib import Path


def ensure_repo_paths(current_file: str) -> Path:
    file_path = Path(current_file).resolve()
    repo_root: Path | None = None
    for parent in file_path.parents:
        if (parent / "src").is_dir() and (parent / "demo").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError("unable to locate repository root for demo bootstrap")

    demo_root = repo_root / "demo"
    src_root = repo_root / "src"
    for path in (str(src_root), str(demo_root)):
        if path not in sys.path:
            sys.path.insert(0, path)
    return repo_root


def print_processing_line(context, value: str) -> None:
    if not context.value_tokens:
        print(f"Processing {context.option}")
        return

    if len(context.value_tokens) == 1:
        print(f'Processing {context.option} with value "{value}"')
        return

    joined = ",".join(f'"{token}"' for token in context.value_tokens)
    print(f"Processing {context.option} with values [{joined}]")
