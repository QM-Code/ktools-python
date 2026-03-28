# API Guide

This page summarizes the Python public API in [`src/ktrace`](../src/ktrace).

## Core Types

| Type | Purpose |
| --- | --- |
| `ktrace.TraceLogger` | Library-facing source object that owns a trace namespace and its declared channels. |
| `ktrace.Logger` | Executable-facing runtime that owns channel registration, selector enablement, and formatted output. |
| `ktrace.OutputOptions` | Output-format toggles for filenames, line numbers, function names, and timestamps. |
| `ktrace.Color()` | Normalizes a named trace color token. |

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
trace.addChannel("net")
trace.addChannel("cache", ktrace.Color("Gold3"))
trace.addChannel("deep.branch.leaf")
```

Channels must use dotted identifier paths.

### Namespace And Enablement

```python
trace.getNamespace()
trace.shouldTraceChannel("net")
```

`shouldTraceChannel()` returns `False` until the trace logger is attached to a
`ktrace.Logger`.

### Trace Output

```python
trace.trace("net", "connected to {}", host)
trace.traceChanged("state", state_key, "state changed to {}", state)
```

`traceChanged()` suppresses repeated output only when the same call site emits
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
logger.addTraceLogger(app_trace)
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
    trace.addChannel("net", ktrace.Color("DeepSkyBlue1"))
    _TRACE_LOGGER = trace
    return _TRACE_LOGGER
```

### Channel Enablement

```python
logger.enableChannel(app_trace, ".app")
logger.enableChannels("*.{net,io}")
logger.disableChannel(app_trace, ".app")
logger.disableChannels("alpha.cache")
```

Selector forms supported by the current Python implementation include:

- `.channel` for a local channel in the provided local namespace
- `namespace.channel`
- wildcard segments inside a qualified selector, such as `*.*` or `alpha.*.*`
- brace sets per segment, such as `*.{net,io}` or `{alpha,beta}.*`

Additional rules:

- bare `*` is invalid; use a qualified selector such as `.*` or `*.*`
- leading-dot selectors require a local namespace context
- `enableChannels(...)` and `disableChannels(...)` accept CSV selector lists
- unmatched selectors produce a warning log rather than raising

### Querying State

```python
logger.shouldTraceChannel(app_trace, ".app")
logger.getNamespaces()
logger.getChannels("alpha")
```

### Output Formatting

```python
options = logger.getOutputOptions()
options.timestamps = True
logger.setOutputOptions(options)
```

When filename output is enabled:

- `filenames + line_numbers` renders `[file:line]`
- adding `function_names` renders `[file:line:function]`

### CLI Integration

```python
parser.addInlineParser(logger.makeInlineParser(app_trace))
```

`makeInlineParser()` exposes:

- `--trace <channels>`
- `--trace-examples`
- `--trace-namespaces`
- `--trace-channels`
- `--trace-colors`
- `--trace-files`
- `--trace-functions`
- `--trace-timestamps`
