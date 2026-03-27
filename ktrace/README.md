# Karma Trace Logging SDK

`ktrace` is the Python tracing and operational logging layer for the ktools
ecosystem.

It follows the same high-level model as the C++ implementation:

- library-facing `TraceLogger` sources with named channels
- executable-facing `Logger` runtime state for selector enablement and output
- `kcli` integration through `logger.makeInlineParser(...)`
- developer/operator output rather than end-user UI text

## Documentation

- [Overview and quick start](docs/index.md)
- [API guide](docs/api.md)
- [Demo overview](demo/README.md)

## Build SDK

Build from the `ktools-python/` workspace root with the local build tool:

```bash
./kbuild/kbuild.py --batch ktrace --build-latest
```

SDK output:

- `build/latest/sdk/python/ktrace`
- `build/latest/sdk/lib/cmake/KtraceSDK`

## Build And Test Demos

```bash
python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests
```

Demo entrypoints from this repo root:

```bash
python3 demo/bootstrap/main.py --trace '.*'
python3 demo/exe/core/main.py --trace '*.*'
python3 demo/exe/omega/main.py --trace '*.{net,io}'
```

Trace CLI examples:

```bash
python3 demo/exe/core/main.py --trace '.*'
python3 demo/exe/omega/main.py --trace '*.*'
python3 demo/exe/omega/main.py --trace '*.{net,io}'
python3 demo/exe/omega/main.py --trace-namespaces
python3 demo/exe/omega/main.py --trace-channels
python3 demo/exe/omega/main.py --trace-colors
```

## API Model

`TraceLogger` is the namespace-bearing source object:

```python
import ktrace

trace = ktrace.TraceLogger("alpha")
trace.addChannel("net", ktrace.Color("DeepSkyBlue1"))
trace.addChannel("cache", ktrace.Color("Gold3"))
```

`Logger` owns the runtime registry, selector state, and formatting:

```python
logger = ktrace.Logger()
logger.addTraceLogger(trace)
logger.enableChannels("alpha.*")
```

## Behavior Highlights

- trace output is channel-gated and disabled by default
- `info()`, `warn()`, and `error()` are always visible once the trace source is attached to a `Logger`
- selector matching supports local selectors, namespace-qualified selectors, `*`, and brace sets such as `*.{net,io}`
- unmatched selectors produce warning output instead of raising
- `makeInlineParser()` exposes `--trace`, `--trace-examples`, `--trace-namespaces`, `--trace-channels`, `--trace-colors`, `--trace-files`, `--trace-functions`, and `--trace-timestamps`

## Demo Layout

- `demo/bootstrap/` minimal logger and inline-parser smoke test
- `demo/sdk/{alpha,beta,gamma}` reusable demo trace sources
- `demo/exe/core/` local executable tracing plus imported alpha tracing
- `demo/exe/omega/` combined local, alpha, beta, and gamma tracing

The demos are covered by subprocess-based CLI tests under `demo/tests/`.

## Coding Agents

If you are using a coding agent, read the workspace-level agent instructions
first and then follow the local repo layout.
