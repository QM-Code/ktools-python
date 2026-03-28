# `kbuild` In `ktools-python`

The Python workspace uses the shared `kbuild` command model for batch builds
and workspace orchestration.

## Current Status

- the checked-out workspace does not currently contain a separate `kbuild/`
  implementation directory
- the documented workflow assumes the shared `kbuild` command is available on
  `PATH`
- Python component docs still describe direct `python3 -m unittest` execution
  where that is the clearest validation path
