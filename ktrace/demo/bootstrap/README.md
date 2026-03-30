# Bootstrap Demo

Minimal logger and inline-parser smoke test for Python `ktrace`.

This demo shows the executable-side setup:

- create a `ktrace.Logger`
- create a local `ktrace.TraceLogger("bootstrap")`
- add a local `app` channel
- attach the trace source to the logger
- enable a local selector and expose trace CLI controls through `logger.build_inline_parser(...)`
