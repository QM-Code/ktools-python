# ktools-python

`ktools-python/` is the Python workspace for the broader ktools ecosystem.

It is the root entrypoint for Python implementations of the ktools libraries.

## Current Contents

This workspace currently contains:

- `kbuild/`
- `kcli/`
- `ktrace/`

## Build Model

Use the workspace-local `kbuild` entry script from this directory:

```bash
./kbuild/kbuild.py --batch kcli ktrace --build-latest
```

Use the relevant child repo when testing a specific Python implementation.

Typical child-repo test commands:

```bash
cd kcli
python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests

cd ../ktrace
python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests
```

The Python workspace keeps its own local copy of `kbuild` under `kbuild/`.

## Where To Go Next

For concrete Python API and implementation details, use the docs in the relevant child repo.

Current implementation:

- [kbuild](kbuild)
- [kcli](kcli)
- [ktrace](ktrace)
