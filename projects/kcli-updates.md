# Python kcli Project

## Mission

Bring `ktools-python/kcli/` up to the C++ reference standard while preserving
the current Python package shape and the underscore-based private module
boundary.

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

- The package split is sensible, but `kcli/src/kcli/_process.py` is too large.
- Test coverage is concentrated in `kcli/tests/test_kcli.py`.
- Tracked build output exists in `kcli/build/latest` and demo build trees.
- The repo contains CMake-related packaging/build files that should be reviewed
  to make sure they support, rather than obscure, the Python implementation.

## Work Plan

1. Refactor the largest modules.
- Split `_process.py` along coherent boundaries such as token collection,
  invocation planning, and help rendering if that improves readability.
- Keep `_api.py`, `_normalize.py`, and `_model.py` focused on their current
  responsibilities.

2. Break up the tests.
- Replace the single large `tests/test_kcli.py` file with smaller test modules
  grouped by API behavior, parsing rules, aliases, inline roots, and error
  semantics.
- Preserve the existing breadth of coverage.
- Keep `demo/tests/` as separate end-to-end validation.

3. Review build and packaging structure.
- Keep only the packaging/build files that are genuinely needed.
- Remove tracked generated output from `build/latest` and demo build trees.
- If CMake-based staging is still required, document its role clearly so it does
  not look like accidental baggage.

4. Audit behavior parity with C++.
- Match documented semantics for alias preset tokens, inline-root help, required
  values that begin with `-`, error formatting, and validation-before-handler
  execution.
- Add direct tests when behavior is presently covered only by demos.

5. Keep demos useful and readable.
- Preserve the current bootstrap/sdk/exe role split.
- Make demo modules easy for other language agents to compare with their own.

## Constraints

- Preserve the current public package API exported from `src/kcli/__init__.py`.
- Keep private implementation details private unless exposure is necessary.
- Avoid introducing framework-heavy packaging patterns.

## Validation

- `cd ktools-python/kcli && python3 -m unittest discover -s tests`
- `cd ktools-python/kcli && python3 -m unittest discover -s demo/tests`
- `cd ktools-python && kbuild --batch kcli --build-latest`
- Run the demo commands listed in `ktools-python/kcli/README.md`

## Done When

- The parser implementation is split into readable modules.
- Unit tests are organized by behavior instead of by accumulation.
- Packaging/build mechanics no longer distract from the actual Python library.
