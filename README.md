# ktools-python

`ktools-python/` is the Python workspace for the broader ktools ecosystem.

It is the root entrypoint for Python implementations of the ktools libraries.

## Current Contents

This workspace currently contains:

- `kcli/`
- `ktrace/`

## Build Model

Use the shared `kbuild` tool from this workspace checkout:

```bash
python3 ../kbuild/kbuild.py --batch kcli ktrace --build-latest
```

If `kbuild` is already on your `PATH`, the equivalent command is:

```bash
kbuild --batch kcli ktrace --build-latest
```

Use the relevant child repo when testing a specific Python implementation.

Typical child-repo test commands:

```bash
cd kcli
python3 -B -m unittest discover -s tests
python3 -B -m unittest discover -s demo/tests

cd ../ktrace
python3 -B -m unittest discover -s tests
python3 -B -m unittest discover -s demo/tests
```

## Where To Go Next

For concrete Python API and implementation details, use the docs in the relevant child repo.

Current implementation:

- [kcli](kcli)
- [ktrace](ktrace)
