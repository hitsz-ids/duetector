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

Comment style is [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

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

## Generating config

Use script to generate config after add tracer/filter...

```bash
python duetector/tools/config_generator.py
```

## Build Docs

Install docs dependencies

```bash
pip install -e .[docs]
```

Build docs

```bash
make clean && make html
```

Use [start-docs-host.sh](dev-tools/start-docs-host.sh) to deploy a local http server to view the docs

```bash
cd ./dev-tools && ./start-docs-host.sh
```

Access `http://localhost:8080` for docs.


## Contributing a new tracer/filter/collector/analyzer

1. Create a new file in `duetector/tracer`, `duetector/filter`, `duetector/collector` or `duetector/analyzer` directory, with the name `{name}.py`
2. Implement the new tracer/filter/collector/analyzer
3. Add the new tracer/filter/collector to `registers` list in `duetector/tracer/register.py`, `duetector/filter/register.py`, `duetector/collector/register.py` or `duetector/analyzer/register.py`
4. Test the new tracer/filter/collector/analyzer
5. Generate new static config file with `python duetector/tools/config_generator.py`

Another way to add a new tracer/filter/collector/analyzer is to use our extension mechanism, see [Extension](./examples/extension). This is not required a change to the duetector codebase and you will mantain the extension by yourself.
