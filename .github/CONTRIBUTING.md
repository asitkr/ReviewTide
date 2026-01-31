# Contributing to ReviewTide

Thanks for considering a contribution. ReviewTide is an offline analyzer: it
reads git logs and PR exports and never calls a forge API.

## Development setup

- Python 3.11+. The package uses the standard library only.

```bash
python -m compileall -q src
python -m pytest -q
PYTHONPATH=src python -m reviewtide --help
```

## Before you open a pull request

1. Compile and the full test suite must pass.
2. Every new metric needs a fixture, a test and a paragraph in the README
   explaining what the number means and what it does not.
3. Keep the package dependency-free.

<!-- draft note 1257 -->
