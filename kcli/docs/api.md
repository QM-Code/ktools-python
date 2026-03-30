# API Guide

This page summarizes the Python public API in [`src/kcli`](../src/kcli).

## Core Types

| Type | Purpose |
| --- | --- |
| `kcli.Parser` | Owns top-level handlers, aliases, positional handling, and inline parser registration. |
| `kcli.InlineParser` | Defines an inline root such as `--build` plus its `--build-*` handlers. |
| `kcli.HandlerContext` | Metadata passed to flag, value, and positional handlers. |
| `kcli.CliError` | Raised by `parse()` for invalid CLI input and handler failures. |

## HandlerContext

`HandlerContext` is passed to every registered handler.

| Field | Meaning |
| --- | --- |
| `root` | Inline root name without leading dashes, such as `build`. Empty for top-level and positional handlers. |
| `option` | Effective option token after alias expansion, such as `--verbose` or `--build-profile`. |
| `command` | Normalized command name without leading dashes. Empty for positional dispatch and bare-root value handlers. |
| `value_tokens` | Effective value tokens after alias preset expansion. |

## CliError

`CliError(option, message)` is raised by `parse()` when:

- the command line is invalid
- a registered option handler raises
- the positional handler raises

`.option` returns the option token associated with the failure when one is
available.

## InlineParser

### Construction

```python
build = kcli.InlineParser("--build")
build = kcli.InlineParser("build")
```

Both forms are accepted.

### Root Control

```python
build.set_root("--newbuild")
```

This changes the inline root after construction.

### Root Value Handler

```python
build.set_root_value_handler(on_root)
build.set_root_value_handler(on_root, "<selector>", "Select build targets.")
```

Use this when the bare root should accept a value instead of only printing help.

### Inline Handlers

```python
build.set_handler("-flag", on_flag, "Enable build flag.")
build.set_handler("-profile", on_profile, "Set build profile.")
build.set_optional_value_handler("-enable", on_enable, "Enable build mode.")
```

Inline options can be written in either form:

- short inline form: `-profile`
- fully-qualified form: `--build-profile`

## Parser

### Top-Level Handlers

```python
parser.set_handler("--verbose", on_verbose, "Enable verbose logging.")
parser.set_handler("--output", on_output, "Set output target.")
parser.set_optional_value_handler("--color", on_color, "Set or auto-detect color output.")
```

Top-level options may be provided as either:

- `"verbose"`
- `"--verbose"`

`set_handler(...)` inspects the callable arity:

- one-argument handlers are treated as flags
- two-argument handlers are treated as required-value handlers

### Aliases

```python
parser.add_alias("-v", "--verbose")
parser.add_alias("-c", "--config-load", ["user-file"])
```

Rules:

- aliases use single-dash form such as `-v`
- alias targets use double-dash form such as `--verbose`
- preset tokens are prepended to the handler's effective `value_tokens`

### Positional Handler

```python
parser.set_positional_handler(on_positionals)
```

The positional handler receives remaining non-option tokens in
`context.value_tokens`.

### Inline Parser Registration

```python
parser.add_inline_parser(build)
```

Duplicate inline roots are rejected.

### Parse Entry Points

```python
parser.parse_or_exit(argv)
parser.parse(argv)
```

`parse_or_exit()`

- preserves the caller's `argv`
- prints errors to `stderr`
- exits with code `2`

`parse()`

- preserves the caller's `argv`
- raises `kcli.CliError`
- does not execute handlers until the parse validates
