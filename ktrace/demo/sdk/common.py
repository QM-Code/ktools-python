from __future__ import annotations

import sys

from pathlib import Path


def ensure_workspace_paths(current_file: str) -> Path:
    file_path = Path(current_file).resolve()
    repo_root: Path | None = None
    for parent in file_path.parents:
        if (parent / "src").is_dir() and (parent / "demo").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError("unable to locate repository root for demo bootstrap")

    workspace_root = repo_root.parent
    demo_root = repo_root / "demo"
    ktrace_src_root = repo_root / "src"
    kcli_src_root = workspace_root / "kcli" / "src"

    for path in (
        str(ktrace_src_root),
        str(demo_root),
        str(kcli_src_root),
    ):
        if path not in sys.path:
            sys.path.insert(0, path)
    return repo_root
