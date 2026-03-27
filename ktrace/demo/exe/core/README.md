# Core Demo

Basic local-plus-imported tracing showcase for Python `ktrace` and the alpha demo SDK.

This demo shows:

- executable-local tracing defined with a local `TraceLogger("core")`
- imported SDK tracing added via the alpha trace source
- logger-managed selector state and output formatting
- CLI integration through `parser.addInlineParser(logger.makeInlineParser(local_trace_logger))`
