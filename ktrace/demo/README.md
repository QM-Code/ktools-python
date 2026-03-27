# Python Demos

Python equivalents of the C++ `ktrace` demos.

Structure:

- `bootstrap/` minimal import and inline-parser smoke test
- `sdk/` reusable demo trace sources
- `exe/` executable integration demos
- `tests/` subprocess-driven CLI checks

Run examples from the repo root:

```bash
python3 demo/bootstrap/main.py --trace '.*'
python3 demo/exe/core/main.py --trace '*.*'
python3 demo/exe/omega/main.py --trace '*.{net,io}'
python3 -m unittest discover -s demo/tests
```
