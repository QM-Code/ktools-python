# Python Updates

## Mission

Keep `ktools-python/` readable, parity-checked, and clearly Pythonic while
preserving the current public package surfaces and private-module boundaries
across both `kcli` and `ktrace`.

## Required Reading

- `../ktools/AGENTS.md`
- `AGENTS.md`
- `README.md`
- `kcli/AGENTS.md`
- `kcli/README.md`
- `kcli/demo/README.md`
- `ktrace/AGENTS.md`
- `ktrace/README.md`
- `ktrace/docs/api.md`
- `ktrace/docs/behavior.md`
- `ktrace/demo/README.md`
- `../ktools-cpp/kcli/README.md`
- `../ktools-cpp/kcli/docs/behavior.md`
- `../ktools-cpp/kcli/cmake/tests/kcli_api_cases.cpp`
- `../ktools-cpp/ktrace/README.md`
- `../ktools-cpp/ktrace/include/ktrace.hpp`
- `../ktools-cpp/ktrace/src/ktrace/cli.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_channel_semantics_test.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_format_api_test.cpp`
- `../ktools-cpp/ktrace/cmake/tests/ktrace_log_api_test.cpp`

## kcli Focus

- Keep the build and staging layer clearly subordinate to the Python package.
- Add the missing bootstrap demo CLI test so demo coverage spans bootstrap,
  core, and omega.
- Re-audit parser parity with C++ for alias preset tokens, inline-root help,
  required values beginning with `-`, double-dash rejection, error formatting,
  and validation-before-handler execution.
- Keep `_process*` module boundaries coherent so one file does not absorb too
  many responsibilities again.

## ktrace Focus

- Remove Python cache noise from the source tree and keep it from returning.
- Review whether `src/ktrace/_api.py` should be split further into smaller,
  coherent modules.
- Re-audit selector parsing, unmatched-selector warnings, logger and
  trace-source attachment, output options, and `makeInlineParser(...)`
  behavior against the C++ contract.
- Keep docs aligned with the current self-contained demo structure.

## Cross-Cutting Rules

- Preserve the public APIs exported from `src/kcli/__init__.py` and
  `src/ktrace/__init__.py`.
- Do not introduce a shared demo helper layer.
- Keep caches and generated output out of version control.

## Validation

- `cd ktools-python/kcli && python3 -m unittest discover -s tests`
- `cd ktools-python/kcli && python3 -m unittest discover -s demo/tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s demo/tests`
- `cd ktools-python && kbuild --batch kcli ktrace --build-latest`
- Run the demo commands listed in each repo README

## Done When

- Demo coverage includes the bootstrap path.
- Public and private module boundaries are easy to follow.
- `kcli` and `ktrace` are both easy to compare with the C++ contract.
