# Development Guide

## Code Style and Lint

We use [black](https://github.com/psf/black) as the code formatter, the best way to use it is to install the pre-commit hook, it will automatically format the code before each commit

Install pre-commit before commit

```bash
pip install pre-commit
pre-commit install
```

Pre-commit will automatically format the code before each commit, It can also be executed manually on all files

```bash
pre-commit run --all-files
```

## Install Locally with Test Dependencies

```bash
pip install -e .[test]
```

## Unittest

We use pytest to write unit tests, and use pytest-cov to generate coverage reports

```bash
pytest -v # Run unit-test
pytest --cov=duetector # Generate coverage reports
```

Run unit-test before PR, **ensure that new features are covered by unit tests**

## Typing

(Optional, python<=3.10) Use [pytype](https://github.com/google/pytype) to check typed

```
pytype ./duetector
```
