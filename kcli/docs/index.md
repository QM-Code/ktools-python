# kcli Python

`kcli` is a compact Python library for executable startup and command-line
parsing. It is intentionally opinionated about normal CLI behavior:

- parse first
- fail early on invalid input
- do not run handlers until the full command line validates
- preserve the caller's `argv`
- support grouped inline roots such as `--trace-*` and `--config-*`

## Start Here

- [API guide](api.md)
- [Parsing behavior](behavior.md)
- [Examples](examples.md)

## Typical Flow

```python
import kcli


def on_verbose(context: kcli.HandlerContext) -> None:
    pass


def on_profile(context: kcli.HandlerContext, value: str) -> None:
    pass


parser = kcli.Parser()
build = kcli.InlineParser("--build")

build.set_handler("-profile", on_profile, "Set build profile.")

parser.add_inline_parser(build)
parser.add_alias("-v", "--verbose")
parser.set_handler("--verbose", on_verbose, "Enable verbose logging.")

argv = ["tool", "--verbose", "--build-profile", "debug"]
parser.parse_or_exit(argv)
```

## Core Concepts

`Parser`

- owns top-level handlers, aliases, inline parser registrations, and the single
  parse pass

`InlineParser`

- defines one inline root namespace such as `--alpha`, `--trace`, or `--build`

`HandlerContext`

- exposes the effective option, command, root, and value tokens seen by the
  handler after alias expansion

`CliError`

- used by `parse()` to surface invalid CLI input and handler failures

## Which Entry Point Should I Use?

Use `parse_or_exit()` when:

- you are in a normal executable startup path
- invalid CLI input should print a standardized error and exit with code `2`
- you do not need custom formatting or recovery

Use `parse()` when:

- you want to customize error formatting
- you want custom exit codes
- you want to intercept and test parse failures directly

## Build And Explore

```bash
python3 ../kbuild/kbuild.py --batch kcli --build-latest
python3 -B demo/exe/core/main.py --alpha-message "hello"
python3 -B demo/exe/omega/main.py --build
python3 -B -m unittest discover -s tests
```

## Working References

If you want complete runnable examples, start with:

- [`../demo/bootstrap/main.py`](../demo/bootstrap/main.py)
- [`../demo/sdk/alpha.py`](../demo/sdk/alpha.py)
- [`../demo/exe/core/main.py`](../demo/exe/core/main.py)
- [`../demo/exe/omega/main.py`](../demo/exe/omega/main.py)
- [`../tests/test_kcli.py`](../tests/test_kcli.py)

The public API contract lives in [`../src/kcli`](../src/kcli).
