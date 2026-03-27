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

```bash
kbuild --build-latest
```

SDK output:

- `build/latest/sdk/python/ktrace`
- `build/latest/sdk/lib/cmake/KtraceSDK`

## Build And Test Demos

```bash
kbuild --build-latest
kbuild --build-demos

python3 -m unittest discover -s tests
python3 -m unittest discover -s demo/tests
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

## Coding Agents

If you are using a coding agent, read the workspace-level agent instructions
first and then follow the local repo layout.
