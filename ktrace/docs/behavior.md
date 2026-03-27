# ktrace Python Behavior

This page collects the Python `ktrace` runtime rules that matter in practice.

## Trace Source Attachment

- `TraceLogger` instances are library-facing sources of namespaces and channels
- `Logger` owns the executable-facing runtime registry, selector state, and
  final output
- a `TraceLogger` may only be attached to one `Logger`

When multiple trace sources register the same qualified channel on one logger:

- duplicate default-color registrations are accepted
- an explicit color may replace a previously-default color
- conflicting explicit colors are rejected

## Selector Semantics

Selectors are resolved against channels already registered on the logger.

Supported forms include:

- local selectors such as `.app`
- namespace-qualified selectors such as `alpha.net`
- wildcard segments such as `*.*` or `*.*.*.*`
- brace sets such as `*.{net,io}` or `{alpha,beta}.*`

Additional rules:

- empty selector lists are rejected
- unmatched selectors emit warning output instead of raising
- unregistered channels remain disabled even if a selector pattern would
  otherwise match them

## Runtime Channel Queries

`Logger.shouldTraceChannel(...)` and `TraceLogger.shouldTraceChannel(...)` return
`False` for:

- unattached trace sources
- unregistered channels
- invalid runtime channel names

This keeps query helpers non-throwing in normal runtime usage.

## Formatting Rules

Message formatting supports:

- sequential `{}` placeholders
- escaped braces `{{` and `}}`
- boolean values formatted as `true` and `false`

Invalid format strings raise `ValueError`, including:

- too few arguments
- too many arguments
- unmatched `{` or `}`
- unsupported tokens such as `{:x}`

## Output Formatting

Trace output is channel-gated and disabled by default.

Operational logs from `info()`, `warn()`, and `error()` are always visible once
the trace source is attached to a logger.

`OutputOptions` controls:

- timestamps
- filenames
- line numbers
- function names

These options affect both trace output and operational logs.
