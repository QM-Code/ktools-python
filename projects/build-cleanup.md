# Python Build Cleanup Project

## Mission

Add a Python-specific residual checker to `kbuild`, then make the Python
workspace stop generating bytecode/cache artifacts outside `build/`.

This task spans both `ktools-python/` and the sibling shared build repo
`../kbuild/`.

## Required Reading

- `../ktools/AGENTS.md`
- `AGENTS.md`
- `README.md`
- `../kbuild/AGENTS.md`
- `../kbuild/README.md`
- `../kbuild/libs/kbuild/residual_ops.py`
- `../kbuild/libs/kbuild/backend_ops.py`
- `../kbuild/libs/kbuild/` backend files as reference
- `../kbuild/tests/test_java_residuals.py`
- `kcli/AGENTS.md`
- `kcli/README.md`
- `ktrace/AGENTS.md`
- `ktrace/README.md`

## Current Gaps

- `kbuild` does not yet have a Python backend residual checker.
- The Python workspace currently has cache noise such as `__pycache__/` and
  `*.pyc` outside `build/`.
- Python demo/test flows can easily regenerate that cache noise unless the
  runtime environment is controlled deliberately.

## Work Plan

1. Add the Python residual checker in `kbuild`.
- Follow the Java checker structure, but make it Python-appropriate.
- Detect real Python-generated residuals outside `build/`, such as
  `__pycache__/`, `*.pyc`, or equivalent interpreter cache output.
- Keep the checker narrow and focused on artifacts the build/test/demo flow can
  actually generate.

2. Add focused `kbuild` tests.
- Add tests for build refusal and `--git-sync` refusal when Python cache
  artifacts appear outside `build/`.
- Add a positive case showing that staged output inside `build/` is allowed.

3. Audit the actual Python workspace build flow.
- Build and test `kcli/` and `ktrace/` through the normal shared workflows.
- Identify where bytecode/cache artifacts are being written into the source
  tree.
- Fix the flow so those artifacts are not generated outside `build/`.

4. Clean up real residuals.
- Remove existing `__pycache__/`, `*.pyc`, and similar generated files from the
  workspace where they do not belong.
- Tighten ignore rules only after the actual generation path is fixed.

5. Keep docs aligned.
- Update `kbuild` docs if the checker needs backend-specific mention.
- Update local docs if they currently recommend workflows that regenerate
  source-tree Python cache output.

## Constraints

- Do not accept source-tree Python caches as normal.
- Prefer preventing bytecode generation in the workspace build/test flow over
  merely ignoring the results.
- Keep the checker and tests easy to reason about.

## Validation

- Run the new Python residual tests in `../kbuild`
- `cd ktools-python && kbuild --batch --build-latest`
- `cd ktools-python/kcli && python3 -m unittest discover -s tests`
- `cd ktools-python/kcli && python3 -m unittest discover -s demo/tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s tests`
- `cd ktools-python/ktrace && python3 -m unittest discover -s demo/tests`
- Confirm the workspace stays free of Python cache artifacts outside `build/`

## Done When

- `kbuild` rejects Python cache residuals outside `build/`.
- The Python workspace no longer generates those residuals in normal use.
- Build and git-sync hygiene are enforced automatically.
