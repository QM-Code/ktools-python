# Python ktrace Project

## Mission

Keep `ktools-python/ktrace/` readable, parity-checked, and clearly Pythonic
while preserving the current public package surface and private-module
boundary.

## Required Reading

- `../ktools/AGENTS.md`
- `AGENTS.md`
- `ktrace/AGENTS.md`
- `ktrace/README.md`
- `ktrace/docs/api.md`
- `ktrace/docs/behavior.md`
- `ktrace/demo/README.md`
- `../ktools-cpp/ktrace/README.md`
- `../ktools-cpp/ktrace/include/ktrace.hpp`
- `../ktools-cpp/ktrace/src/ktrace/cli.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_channel_semantics_test.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_format_api_test.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_log_api_test.cpp`

## Current Gaps

- The shared demo layer is gone and bootstrap CLI coverage exists, but Python
  cache noise such as `__pycache__/` and `*.pyc` is still showing up in the
  source tree.
- `src/ktrace/_api.py` still centralizes a large amount of behavior.
- The implementation still needs a deliberate parity audit against the full
  C++ contract for selectors, output formatting, logging behavior, and CLI
  integration.
- Docs and demo layout should be checked so they reflect the current
  self-contained demo structure directly.

## Work Plan

1. Clean up Python cache noise.
- Remove `__pycache__/`, `*.pyc`, and similar generated files from the source
  tree where they do not belong.
- Keep the repo readable as handwritten source, tests, and demos rather than a
  mix of source and interpreter cache output.

2. Revisit the largest module boundary.
- Review whether `_api.py` should be split further into smaller, coherent
  modules.
- Preserve the public package surface exported from `src/ktrace/__init__.py`.

3. Continue the parity audit.
- Verify channel registration, selector parsing, bare `*` rejection,
  unmatched-selector warnings, logger/trace-source attachment, output options,
  and `makeInlineParser(...)` behavior against the C++ contract.
- Add direct tests where behavior is currently covered only indirectly.

4. Keep demos and docs aligned.
- Confirm that bootstrap/sdk/exe demo roles still match the reference.
- Update docs if any current behavior or layout still requires inference.

## Constraints

- Preserve the public package API exported from `src/ktrace/__init__.py`.
- Keep private implementation details private unless exposure is necessary.
- Keep the demos readable as separate entities, not one shared helper layer.

## Validation

- `cd ktools-python/ktrace && python3 -m unittest discover -s tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s demo/tests`
- `cd ktools-python && kbuild --batch ktrace --build-latest`
- Run the demo commands listed in `ktools-python/ktrace/README.md`

## Done When

- Python cache noise no longer obscures the repo.
- Public/private module boundaries are easy to follow.
- The Python repo is easy to compare with the C++ contract.
