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
app_trace.addChannel("app", ktrace.Color("BrightCyan"))
app_trace.addChannel("startup", ktrace.Color("BrightYellow"))

logger.addTraceLogger(app_trace)

parser = kcli.Parser()
parser.addInlineParser(logger.makeInlineParser(app_trace))

argv = ["tool", "--trace", ".app"]
parser.parseOrExit(len(argv), argv)

app_trace.trace("app", "cli processing enabled")
app_trace.info("service starting")
```

## Main Behaviors

- trace output is channel-gated
- operational logs from `info()`, `warn()`, and `error()` are always visible
- selectors support local forms such as `.app` and wildcard forms such as `*.*`
- output formatting can include timestamps, filenames, line numbers, and
  function names
- `makeInlineParser()` exposes the `--trace*` CLI surface through `kcli`

For the Python public surface, see [api.md](api.md).
