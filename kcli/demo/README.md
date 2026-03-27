# Python Demos

Python equivalents of the C++ demos under `demo/`.

Structure:

- `bootstrap/` minimal import and parse smoke test
- `sdk/` reusable inline parser modules
- `exe/` executable integration demos
- `tests/` subprocess-driven CLI checks for the Python demos

Demo pages:

- [bootstrap/README.md](bootstrap/README.md)
- [sdk/alpha/README.md](sdk/alpha/README.md)
- [sdk/beta/README.md](sdk/beta/README.md)
- [sdk/gamma/README.md](sdk/gamma/README.md)
- [exe/core/README.md](exe/core/README.md)
- [exe/omega/README.md](exe/omega/README.md)

Run examples from the repo root:

```bash
python3 demo/bootstrap/main.py --verbose
python3 demo/exe/core/main.py --alpha-message hello
python3 demo/exe/omega/main.py --newgamma-tag prod
python3 -m unittest discover -s demo/tests
```
