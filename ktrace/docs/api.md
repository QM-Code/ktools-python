# API Guide

This page summarizes the Python public API in [`src/ktrace`](../src/ktrace).

## Core Types

| Type | Purpose |
| --- | --- |
| `ktrace.TraceLogger` | Library-facing source object that owns a trace namespace and its declared channels. |
| `ktrace.Logger` | Executable-facing runtime that owns channel registration, selector enablement, and formatted output. |
| `ktrace.OutputOptions` | Output-format toggles for filenames, line numbers, function names, and timestamps. |
| `ktrace.color()` | Normalizes a named trace color token. |

## OutputOptions

```python
options = ktrace.OutputOptions()
options.filenames = True
options.line_numbers = True
options.function_names = True
options.timestamps = True
```

These options affect both trace output and operational logs.

## TraceLogger

### Construction

```python
trace = ktrace.TraceLogger("alpha")
```

The namespace must be a valid selector identifier.

### Channel Registration

```python
trace.add_channel("net")
trace.add_channel("cache", ktrace.color("Gold3"))
trace.add_channel("deep.branch.leaf")
```

Channels must use dotted identifier paths.

### Namespace And Enablement

```python
trace.namespace
trace.is_channel_enabled("net")
```

`is_channel_enabled()` returns `False` until the trace logger is attached to a
`ktrace.Logger`.

### Trace Output

```python
trace.trace("net", "connected to {}", host)
trace.trace_changed("state", state_key, "state changed to {}", state)
```

`trace_changed()` suppresses repeated output only when the same call site emits
the same key repeatedly.

### Operational Logs

```python
trace.info("service started")
trace.warn("retrying connection")
trace.error("startup failed")
```

These logs are not gated by channel selectors.

## Logger

### Attaching Trace Sources

```python
logger = ktrace.Logger()
logger.add_trace_logger(app_trace)
```

A `TraceLogger` may only be attached to one `Logger`.

SDK-style modules will usually expose a shared trace source through a
module-level getter:

```python
_TRACE_LOGGER: ktrace.TraceLogger | None = None


def get_trace_logger() -> ktrace.TraceLogger:
    global _TRACE_LOGGER
    if _TRACE_LOGGER is not None:
        return _TRACE_LOGGER

    trace = ktrace.TraceLogger("alpha")
    trace.add_channel("net", ktrace.color("DeepSkyBlue1"))
    _TRACE_LOGGER = trace
    return _TRACE_LOGGER
```

### Channel Enablement

```python
logger.enable_channel(app_trace, ".app")
logger.enable_channels("*.{net,io}")
logger.disable_channel(app_trace, ".app")
logger.disable_channels("alpha.cache")
```

Selector forms supported by the current Python implementation include:

- `.channel` for a local channel in the provided local namespace
- `namespace.channel`
- wildcard segments inside a qualified selector, such as `*.*` or `alpha.*.*`
- brace sets per segment, such as `*.{net,io}` or `{alpha,beta}.*`

Additional rules:

- bare `*` is invalid; use a qualified selector such as `.*` or `*.*`
- leading-dot selectors require a local namespace context
- `enable_channels(...)` and `disable_channels(...)` accept CSV selector lists
- unmatched selectors produce a warning log rather than raising

### Querying State

```python
logger.is_channel_enabled(app_trace, ".app")
logger.namespaces
logger.channels("alpha")
```

### Output Formatting

```python
options = logger.output_options
options.timestamps = True
logger.output_options = options
```

When filename output is enabled:

- `filenames + line_numbers` renders `[file:line]`
- adding `function_names` renders `[file:line:function]`

### CLI Integration

```python
parser.add_inline_parser(logger.build_inline_parser(app_trace))
```

`build_inline_parser()` exposes:

- `--trace <channels>`
- `--trace-examples`
- `--trace-namespaces`
- `--trace-channels`
- `--trace-colors`
- `--trace-files`
- `--trace-functions`
- `--trace-timestamps`
