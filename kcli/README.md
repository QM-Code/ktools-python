# Karma CLI Parsing SDK

`kcli` is the Python command-line parsing layer in the ktools ecosystem.

It supports two complementary CLI shapes:

- top-level options such as `--verbose`
- inline roots such as `--build-*`, `--trace-*`, or `--config-*`

## Documentation

- [Overview and quick start](docs/index.md)
- [API guide](docs/api.md)
- [Demo overview](demo/README.md)

## Build And Test

```bash
python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests

python3 ../kbuild/kbuild.py --build-latest
```

## Repository Layout

- Public Python package: `src/kcli/`
- Unit tests: `tests/`
- Integration demos: `demo/`

## Coding Agents

Read the workspace instructions first, then use the repo-local docs and tests as
the implementation contract.
