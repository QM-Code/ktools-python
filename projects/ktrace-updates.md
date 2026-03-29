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

- The CMake/kbuild staging layer still tracks a large amount of build output
  under `ktrace/build/latest` and demo build trees.
- `ktrace/demo/sdk/common.py` exists and should not.
- `demo/tests/` does not currently include a bootstrap CLI test.
- The implementation still needs a deliberate parity audit against the full
  C++ contract for selectors, output formatting, logging behavior, and CLI
  integration.

## Work Plan

1. Review the build/staging layer.
- Remove tracked build products and cache noise where they are not genuinely
  required.
- Keep only the packaging/build files that are necessary for shared staging.
- Make the real implementation obviously live in `src/`, `tests/`, and
  `demo/`.

2. Eliminate shared demo code.
- Remove `ktrace/demo/sdk/common.py`.
- Make `demo/sdk/alpha.py`, `demo/sdk/beta.py`, and `demo/sdk/gamma.py`
  self-contained.
- Keep bootstrap-specific logic in `demo/bootstrap/`.
- Keep executable composition logic in `demo/exe/core/` and
  `demo/exe/omega/`.
- Do not replace `common.py` with another shared demo helper.

3. Fill demo-coverage gaps.
- Add a bootstrap demo CLI test so the demo suite covers bootstrap, core, and
  omega behavior consistently.
- Add any other focused demo checks that still depend on manual review.

4. Continue the parity audit.
- Verify channel registration, selector parsing, bare `*` rejection,
  unmatched-selector warnings, logger/trace-source attachment, output options,
  and `makeInlineParser(...)` behavior against the C++ contract.
- Add direct tests where behavior is currently covered only indirectly.

5. Keep internals and hygiene well-bounded.
- Preserve a clear split between public API, selector logic, and formatting.
- Keep caches and generated output out of version control.

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

- The build/staging layer is clearly subordinate to the Python implementation.
- Shared demo code is gone and bootstrap demo coverage exists.
- The Python repo is easy to compare with the C++ contract.
