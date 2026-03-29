# Python Demos

Python equivalents of the C++ `ktrace` demos.

Structure:

- `bootstrap/` minimal import and inline-parser smoke test
- `sdk/` reusable demo trace sources
- `exe/` executable integration demos
- `tests/` subprocess-driven CLI checks

Demo pages:

- [bootstrap/README.md](bootstrap/README.md)
- [sdk/alpha/README.md](sdk/alpha/README.md)
- [sdk/beta/README.md](sdk/beta/README.md)
- [sdk/gamma/README.md](sdk/gamma/README.md)
- [exe/core/README.md](exe/core/README.md)
- [exe/omega/README.md](exe/omega/README.md)

Run examples from the repo root:

```bash
python3 -B demo/bootstrap/main.py --trace '.*'
python3 -B demo/exe/core/main.py --trace '*.*'
python3 -B demo/exe/omega/main.py --trace '*.{net,io}'
python3 -B -m unittest discover -s demo/tests
```
