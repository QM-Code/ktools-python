# ktrace Python

`ktrace` is the Python tracing and operational logging layer in the ktools
stack.

It separates:

- library-facing `TraceLogger` sources that define namespaces and channels
- executable-facing `Logger` runtime state that owns selector enablement and
  output formatting

## Quick Start

```python
import kcli
import ktrace


logger = ktrace.Logger()

app_trace = ktrace.TraceLogger("core")
app_trace.add_channel("app", ktrace.color("BrightCyan"))
app_trace.add_channel("startup", ktrace.color("BrightYellow"))

logger.add_trace_logger(app_trace)

parser = kcli.Parser()
parser.add_inline_parser(logger.build_inline_parser(app_trace))

argv = ["tool", "--trace", ".app"]
parser.parse_or_exit(argv)

app_trace.trace("app", "cli processing enabled")
app_trace.info("service starting")
```

## Main Behaviors

- trace output is channel-gated
- operational logs from `info()`, `warn()`, and `error()` are always visible
- selectors support local forms such as `.app` and wildcard forms such as `*.*`
- conflicting explicit channel-color merges are rejected when multiple trace
  sources register the same qualified channel on one logger
- invalid runtime channel queries return `False`
- output formatting can include timestamps, filenames, line numbers, and
  function names
- `build_inline_parser()` exposes the `--trace*` CLI surface through `kcli`

For the Python public surface, see [api.md](api.md). For the concrete selector,
merge, and formatting rules, see [behavior.md](behavior.md).
