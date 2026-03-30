# ktrace-python

Assume these have already been read:

- `../../ktools/AGENTS.md`
- `../AGENTS.md`

`ktools-python/ktrace/` is the Python implementation of `ktrace`.

## What This Component Owns

This component owns the Python API and implementation details for `ktrace`, including:

- the public Python package under `src/ktrace/`
- selector, formatting, and logging behavior
- Python demos and tests
- SDK packaging metadata for the Python build flow

Cross-language conceptual behavior belongs to `ktools/`. Python workspace
concerns belong to `ktools-python/`.

## Local Bootstrap

When familiarizing yourself with this component, read:

- [README.md](README.md)
- `src/ktrace/*`
- `tests/test_ktrace.py`
- `demo/README.md`

## Build And Test Expectations

- Prefer the shared `kbuild` workflow from the workspace root for builds
- Use direct `python3 -B -m unittest` runs from this component root for fast feedback
- Treat demos under `demo/` as part of the contract, not disposable examples

Useful commands:

```bash
python3 ../kbuild/kbuild.py --batch ktrace --build-latest
python3 -B -m unittest discover -s tests
python3 -B -m unittest discover -s demo/tests
```

## Guidance For Agents

1. Preserve the cross-language `ktrace` behavior model unless the operator explicitly wants a Python-specific deviation.
2. Favor parity with the C++ selector, merge, formatting, and demo contracts when Python behavior is underspecified.
3. Keep logging/output changes deliberate; demos and downstream libraries rely on operator-facing trace behavior.
4. Surface issues or recommendations when you find them.
5. After a coherent batch of changes in `ktools-python/ktrace/`, return to the
   `ktools-python/` workspace root and run `kbuild --git-sync "<message>"`.
