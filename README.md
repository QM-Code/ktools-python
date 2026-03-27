# ktools-python

`ktools-python/` is the Python workspace for the broader ktools ecosystem.

It is the root entrypoint for Python implementations of the ktools libraries.

## Current Contents

This workspace currently contains:

- `kbuild/`
- `kcli/`
- `ktrace/`

## Build Model

Use the relevant child repo when building or testing a specific Python implementation.

The shared build tool for the ecosystem is `kbuild`, exposed on `PATH`, though individual Python repos may also support direct Python-native test or execution flows.

## Where To Go Next

For concrete Python API and implementation details, use the docs in the relevant child repo.

Current implementation:

- [kbuild](kbuild)
- [kcli](kcli)
- [ktrace](ktrace)
