# Karma CLI Parsing SDK

`kcli` is the Python command-line parsing layer in the ktools ecosystem.

It supports two complementary CLI shapes:

- top-level options such as `--verbose`
- inline roots such as `--build-*`, `--trace-*`, or `--config-*`

The Python implementation follows the same core model as the C++ SDK:

- `Parser` for top-level options, aliases, and positionals
- `InlineParser` for one inline root such as `--build`
- full-parse validation before any registered handler executes
- `parseOrExit()` for executable-style handling and `parseOrThrow()` for tests and custom error handling

## Documentation

- [Overview and quick start](docs/index.md)
- [API guide](docs/api.md)
- [Parsing behavior](docs/behavior.md)
- [Examples](docs/examples.md)
- [Demo overview](demo/README.md)

## Build And Test

Build from the `ktools-python/` workspace root with the shared build tool:

```bash
python3 ../kbuild/kbuild.py --batch kcli --build-latest
```

The CMake files in this repo exist only to let `kbuild` stage the Python
package and demo entrypoints into the shared SDK/demo layout. Parser behavior
lives in `src/`, `tests/`, and `demo/`; keep the CMake layer thin.

If `kbuild` is already on your `PATH`, the equivalent command is:

```bash
kbuild --batch kcli --build-latest
```

From this repo root, run the Python tests directly:

```bash
python3 -B -m unittest discover -s tests
python3 -B -m unittest discover -s demo/tests
```

Demo entrypoints from this repo root:

```bash
python3 -B demo/bootstrap/main.py --verbose
python3 -B demo/exe/core/main.py --alpha-message hello
python3 -B demo/exe/omega/main.py --newgamma-tag prod
python3 -B demo/exe/omega/main.py --build
```

## Behavior Highlights

- `parseOrExit()` reports `[error] [cli] ...` to `stderr` and exits with code `2`
- `parseOrThrow()` raises `kcli.CliError`
- bare inline roots such as `--alpha` or `--build` print inline help by default
- root value handlers support bare-root values such as `--trace '.*'`
- required-value handlers may consume a first value token that begins with `-`
- literal `--` is rejected as an unknown option; it is not treated as an option terminator

## Demo Layout

- `demo/bootstrap/` minimal import and parse smoke test
- `demo/sdk/{alpha,beta,gamma}` reusable inline parser modules
- `demo/exe/core/` local app handlers plus the alpha inline parser
- `demo/exe/omega/` combined alpha, beta, gamma, and local build parsers

## Repository Layout

- Public Python package: `src/kcli/`
- Unit tests: `tests/`
- Integration demos: `demo/`

The demos are part of the expected behavior contract and have subprocess-based coverage under `demo/tests/`.

## Coding Agents

Read the workspace instructions first, then use the repo-local docs and tests as
the implementation contract.
