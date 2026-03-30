# Examples

This page shows common Python `kcli` patterns. For complete runnable examples,
also see:

- [`../demo/sdk/alpha.py`](../demo/sdk/alpha.py)
- [`../demo/sdk/beta.py`](../demo/sdk/beta.py)
- [`../demo/sdk/gamma.py`](../demo/sdk/gamma.py)
- [`../demo/exe/core/main.py`](../demo/exe/core/main.py)
- [`../demo/exe/omega/main.py`](../demo/exe/omega/main.py)

## Minimal Executable

```python
import kcli


def on_verbose(context: kcli.HandlerContext) -> None:
    print(f"Processing {context.option}")


parser = kcli.Parser()
parser.add_alias("-v", "--verbose")
parser.set_handler("--verbose", on_verbose, "Enable verbose logging.")
```

## Inline Root With Required And Optional Values

```python
import kcli


def on_profile(context: kcli.HandlerContext, value: str) -> None:
    print(f"profile={value}")


def on_enable(context: kcli.HandlerContext, value: str) -> None:
    print(f"enable={value!r}")


build = kcli.InlineParser("--build")
build.set_handler("-profile", on_profile, "Set build profile.")
build.set_optional_value_handler("-enable", on_enable, "Enable build mode.")

parser = kcli.Parser()
parser.add_inline_parser(build)
```

This enables:

- `--build`
- `--build-profile debug`
- `--build-enable`
- `--build-enable auto`

## Bare Root Value Handler

```python
import kcli


def on_selector(context: kcli.HandlerContext, value: str) -> None:
    print(f"selector={value}")


trace = kcli.InlineParser("--trace")
trace.set_root_value_handler(on_selector, "<channels>", "Trace selected channels.")
```

This enables:

- `--trace`
- `--trace '.app'`
- `--trace '*.{net,io}'`

Behavior:

- `--trace` prints inline help
- `--trace '.app'` invokes `on_selector`

## Alias Preset Tokens

```python
import kcli


def on_config_load(context: kcli.HandlerContext, value: str) -> None:
    print(context.option)
    print(context.value_tokens)
    print(value)


parser = kcli.Parser()
parser.add_alias("-c", "--config-load", ["user-file"])
parser.set_handler("--config-load", on_config_load, "Load config.")
```

This makes:

- `-c settings.json`

behave like:

- `--config-load user-file settings.json`

Inside the handler:

- `context.option` is `--config-load`
- `context.value_tokens` is `["user-file", "settings.json"]`

## Positionals

```python
def on_positionals(context: kcli.HandlerContext) -> None:
    for token in context.value_tokens:
        use_positional(token)


parser.set_positional_handler(on_positionals)
```

The positional handler receives all remaining non-option tokens after option
parsing succeeds.

## Custom Error Handling

If you want your own formatting or exit policy, use `parse()`:

```python
try:
    parser.parse(argv)
except kcli.CliError as exc:
    print(f"custom cli error: {exc}")
    raise SystemExit(2)
```

Use this when:

- you want custom error text
- you want custom logging
- you want a different exit code policy
