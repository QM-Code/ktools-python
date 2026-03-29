# ktools-python

Assume `../ktools/AGENTS.md` has already been read.

`ktools-python/` is the Python workspace for the ktools ecosystem.

## What This Level Owns

This workspace owns Python-specific concerns such as:

- Python package/module layout
- Python build, test, and runtime conventions
- Python-specific API naming and integration patterns
- coordination across Python tool implementations when more than one repo is present

Cross-language conceptual definitions belong at the overview/spec level, not here.

## Current Scope

This workspace currently contains:

- `kcli/`
- `ktrace/`

## Guidance For Agents

1. First determine whether the task belongs at the workspace root or inside a specific implementation repo.
2. Prefer making changes in the narrowest repo that actually owns the behavior.
3. Use the root workspace only for Python-workspace-wide concerns such as root docs or cross-repo coordination.
4. Read the relevant child repo `AGENTS.md` and `README.md` files before changing code in that repo.
5. Use `kbuild` from `PATH` when the operator expects shared build tooling; otherwise follow the local implementation's documented Python flow.

## Git Sync

Use the shared `kbuild` workflow for commit/push sync from this workspace root:

```bash
kbuild --git-sync "<message>"
```

Treat that as the standard sync command unless a more local doc explicitly
overrides it.
After a coherent batch of changes in this workspace or one of its child repos,
return to `ktools-python/` and run that sync command promptly.
