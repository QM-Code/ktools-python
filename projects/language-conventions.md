# Python Language Conventions

## Mission

Refactor `ktools-python/` so the public `kcli` and `ktrace` APIs read like
Python libraries rather than direct translations of the cross-language surface.

Preserve behavior and cross-language capability, but do not preserve
non-Pythonic public naming just for parity. The final public API should be
idiomatic Python.

## Required Reading

- `../ktools/AGENTS.md`
- `AGENTS.md`
- `README.md`
- `kcli/AGENTS.md`
- `kcli/README.md`
- `kcli/src/kcli/__init__.py`
- `kcli/src/kcli/_api.py`
- `ktrace/AGENTS.md`
- `ktrace/README.md`
- `ktrace/src/ktrace/__init__.py`
- `ktrace/src/ktrace/_api.py`
- `../ktools-cpp/kcli/README.md`
- `../ktools-cpp/kcli/docs/behavior.md`
- `../ktools-cpp/kcli/cmake/tests/kcli_api_cases.cpp`
- `../ktools-cpp/ktrace/README.md`
- `../ktools-cpp/ktrace/include/ktrace.hpp`
- `../ktools-cpp/ktrace/src/ktrace/cli.cpp`

## Primary Goals

- Move public method and function names to `snake_case`.
- Remove explicit `argc` from the public parse entrypoints. Public Python parse
  calls should accept `argv` directly.
- Remove Java/C++ carryover names such as `parseOrThrow`, `parseOrExit`,
  `setHandler`, `addInlineParser`, `addTraceLogger`, `enableChannels`,
  `makeInlineParser`, and the capitalized `Color(...)` helper from the final
  public Python surface.
- Audit whether simple getter-style methods should become more idiomatic Python
  names or properties where that materially improves the API.
- Keep the exported package surfaces in `src/kcli/__init__.py` and
  `src/ktrace/__init__.py` coherent and intentional after the refactor.

## Scope

### `kcli`

- Refactor the public parser and inline-parser APIs to idiomatic Python naming.
- Revisit the throwing entrypoint name. Python raises exceptions; the final API
  should not keep `throw` terminology.
- Update docs, demos, and tests so they exercise the new public API directly.
- Keep internal modules private and Pythonic too if a public rename exposes
  awkward carryover names behind the scenes.

### `ktrace`

- Refactor the public logger and trace-source APIs to idiomatic Python naming.
- Replace the capitalized `Color(...)` helper with a Pythonic public name.
- Revisit `get*` and `should*` names where the current spelling feels imported
  rather than native.
- Update CLI integration examples so `ktrace` demonstrates the Pythonic `kcli`
  API rather than the old translated one.

## Rules

- Do not keep a permanent dual API with both camelCase and snake_case.
- If a temporary compatibility shim is useful during the refactor, remove it
  before closing the task unless there is a clearly documented reason to keep
  it.
- Preserve behavior, validation rules, and demo topology.
- Do not weaken parity with the C++ behavior contract while making the Python
  surface more idiomatic.

## Validation

- `cd ktools-python/kcli && python3 -m unittest discover -s tests`
- `cd ktools-python/kcli && python3 -m unittest discover -s demo/tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s demo/tests`
- Run the demo commands listed in each component README.

## Done When

- The public Python APIs look intentionally Pythonic rather than translated.
- Public examples no longer show explicit `argc` handling or camelCase method
  names.
- `kcli` and `ktrace` docs, demos, and tests all use the final Pythonic
  surface consistently.
