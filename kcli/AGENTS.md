# kcli-python

Assume these have already been read:

- `../../ktools/AGENTS.md`
- `../AGENTS.md`

`ktools-python/kcli/` is the Python implementation of `kcli`.

## What This Repo Owns

This repo owns the Python API and implementation details for `kcli`, including:

- the public Python package under `src/kcli/`
- parser and inline-parser behavior
- Python demos and tests
- SDK packaging metadata for the Python build flow

Cross-language conceptual behavior belongs to `ktools/`. Python workspace
concerns belong to `ktools-python/`.

## Local Bootstrap

When familiarizing yourself with this repo, read:

- [README.md](README.md)
- `src/kcli/*`
- `tests/test_kcli.py`
- `demo/README.md`

## Build And Test Expectations

- Prefer the shared `kbuild` workflow from the workspace root for builds
- Use direct `python3 -m unittest` runs from this repo root for fast feedback
- Treat demos under `demo/` as part of the contract, not disposable examples

Useful commands:

```bash
python3 ../kbuild/kbuild.py --batch kcli --build-latest
python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests
```

## Guidance For Agents

1. Preserve the cross-language `kcli` parsing model unless the operator explicitly wants a Python-specific deviation.
2. Keep public API changes deliberate; downstream repos such as `ktrace` depend on this package shape.
3. Prefer aligning behavior with the C++ docs/tests when the Python contract is underspecified.
4. Surface issues or recommendations when you find them.
