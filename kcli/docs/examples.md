# Examples

This page collects complete Python usage examples for the public `kcli` API.

## Top-Level Options

```python
import kcli


def on_verbose(context: kcli.HandlerContext) -> None:
    print(f"Processing {context.option}")


def on_output(context: kcli.HandlerContext, value: str) -> None:
    print(f'Processing {context.option} with value "{value}"')


parser = kcli.Parser()
parser.addAlias("-v", "--verbose")
parser.setHandler("--verbose", on_verbose, "Enable verbose logging.")
parser.setHandler("--output", on_output, "Set output target.")
```

## Inline Root With Value And Optional Value

```python
import kcli


def on_profile(context: kcli.HandlerContext, value: str) -> None:
    print(f"profile={value}")


def on_enable(context: kcli.HandlerContext, value: str) -> None:
    print(f"enable={value!r}")


build = kcli.InlineParser("--build")
build.setHandler("-profile", on_profile, "Set build profile.")
build.setOptionalValueHandler("-enable", on_enable, "Enable build mode.")

parser = kcli.Parser()
parser.addInlineParser(build)
```

The following forms are accepted:

- `--build-profile debug`
- `--build-enable`
- `--build-enable auto`

## Bare Root Value Handler

```python
import kcli


def on_selector(context: kcli.HandlerContext, value: str) -> None:
    print(f"selector={value}")


trace = kcli.InlineParser("--trace")
trace.setRootValueHandler(on_selector, "<channels>", "Trace selected channels.")

parser = kcli.Parser()
parser.addInlineParser(trace)
```

This supports:

- `--trace`
- `--trace '.app'`
- `--trace '*.{net,io}'`

When `--trace` is used without a value, inline help is printed.

## Working References

If you want complete runnable examples, start with:

- `demo/bootstrap/main.py`
- `demo/sdk/alpha.py`
- `demo/exe/core/main.py`
- `demo/exe/omega/main.py`
