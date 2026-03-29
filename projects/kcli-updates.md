# Python kcli Project

## Mission

Keep `ktools-python/kcli/` readable, parity-checked, and clearly Pythonic while
preserving the current public package surface and private-module boundary.

## Required Reading

- `../ktools/AGENTS.md`
- `AGENTS.md`
- `kcli/AGENTS.md`
- `kcli/README.md`
- `kcli/demo/README.md`
- `../ktools-cpp/kcli/README.md`
- `../ktools-cpp/kcli/docs/behavior.md`
- `../ktools-cpp/kcli/cmake/tests/kcli_api_cases.cpp`

## Current Gaps

- The CMake/kbuild staging layer still needs discipline so it supports the
  Python package rather than obscuring it.
- `demo/tests/` does not currently include a bootstrap CLI test.
- The `_process`, `_process_plan`, `_process_values`, and `_process_help`
  split should be kept explicit and coherent as the implementation evolves.
- The implementation still needs a deliberate parity audit against the full C++
  contract and demo behavior.

## Work Plan

1. Review the build/staging layer.
- Keep only the packaging/build files that are genuinely required for shared
  SDK/demo staging.
- Document their role clearly so the real implementation remains obviously in
  `src/`, `tests/`, and `demo/`.

2. Fill demo-coverage gaps.
- Add a bootstrap demo CLI test so the demo suite covers bootstrap, core, and
  omega behavior consistently.
- Add any other focused demo checks that still depend on manual review.

3. Continue the parity audit.
- Verify alias preset tokens, inline-root help, required values beginning with
  `-`, double-dash rejection, error formatting, and
  validation-before-handler execution against the C++ docs/tests.
- Add direct tests where behavior is currently covered only indirectly.

4. Keep parser internals well-bounded.
- Maintain a clear division between planning, value collection, help rendering,
  and top-level parse coordination.
- Avoid letting one `_process*` module absorb too many responsibilities again.

5. Keep repo hygiene tight.
- Preserve the current ignore rules for build output and caches.
- Make sure test/demo cache noise does not drift into version control.

## Constraints

- Preserve the public package API exported from `src/kcli/__init__.py`.
- Keep private implementation details private unless exposure is necessary.
- Avoid introducing framework-heavy packaging patterns.

## Validation

- `cd ktools-python/kcli && python3 -m unittest discover -s tests`
- `cd ktools-python/kcli && python3 -m unittest discover -s demo/tests`
- `cd ktools-python && kbuild --batch kcli --build-latest`
- Run the demo commands listed in `ktools-python/kcli/README.md`

## Done When

- The build/staging layer is clearly subordinate to the Python implementation.
- Demo coverage includes the bootstrap path.
- The Python repo is easy to compare with the C++ contract without digging
  through packaging noise.
