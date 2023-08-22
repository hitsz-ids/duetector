In this example, we will write a simple echo Filter. The Filter will print the tracking data to the console.

Full example and more details can be found in [duetector_echofilter](./duetector_echofilter/)

## 1 Write a Filter

Here we write the echo Filter and set it to not `disabled` by defaylt.

```python
from typing import NamedTuple, Optional
from duetector.filters import Filter

class EchoFilter(Filter):
    default_config = {
        "disabled": False,
    }

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        print(data)
        return data

```

## 2 Register the Filter

```python
from duetector.extension.filter import hookimpl

@hookimpl
def init_filter(config):
    return EchoFilter(config)
```

## 3 Turning the Filter into a package

Here we use `pyproject.toml` as the configuration file.

```toml
# Build with hatch, you can use any build tool you like.
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "duetector-filter"

dependencies = ["duetector"]
dynamic = ["version"]

# This is the entry point for the FilterManager to find the Filter.
[project.entry-points."duetector.filter"]
echofilter = "duetector_echofilter.echo"

[tool.hatch.version]
path = "duetector_echofilter/__init__.py"

```

## 4 Verification

Simply run the following code to verify the Filter is registered.

```python
from duetector.manager import FilterManager
from duetector_echofilter.echo import EchoFilter


assert EchoFilter in (type(c) for c in FilterManager().init())
```

## 5 Configuration

In `config.toml` you can set the Filter to be disabled.

```toml
[filter.EchoFilter]
disabled = true
```

In code, you can use `self.config.{config}` for any configuration. If the configuration is not set, it will use the default value in `self.default_config` or `None`.

Example:

Config the `EchoFilter` to pretty print the tracking data.

```toml
[filter.EchoFilter]
pretty = true
```

In code:

```python
class EchoFilter(Filter):
    default_config = {
        "disabled": False,
        "pretty": False,
    }

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        if self.config.pretty:
            # Use pretty print
            self.pretty_print(data)
        else:
            print(data)
        return data
```
