# kcli Python

`kcli` is a small Python library for building structured CLIs with explicit
support for both ordinary options and namespaced inline roots.

## Core Model

`kcli` exposes two main parser types:

- `Parser` for top-level options, aliases, and positional handling
- `InlineParser` for a root such as `--build` and its `--build-*` options

Handlers are validated first and then executed only after the full command line
parses cleanly.

## Quick Start

```python
import kcli


def on_verbose(context: kcli.HandlerContext) -> None:
    pass


def on_profile(context: kcli.HandlerContext, value: str) -> None:
    pass


parser = kcli.Parser()
build = kcli.InlineParser("--build")

build.setHandler("-profile", on_profile, "Set build profile.")
parser.addInlineParser(build)
parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")

argv = ["tool", "--verbose", "--build-profile", "debug"]
parser.parseOrExit(len(argv), argv)
```

## Main Behaviors

- `parseOrExit()` prints `[error] [cli] ...` and exits with code `2`
- `parseOrThrow()` raises `kcli.CliError`
- bare inline roots such as `--build` print inline help by default
- root value handlers can claim bare-root values such as `--trace '.*'`
- required values may consume a first token that begins with `-`
- aliases can prepend preset value tokens

For the Python public surface, see [api.md](api.md).
