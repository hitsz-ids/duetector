In this example, we will write a simple echo Collector. The Collector will print the tracking data to the console.

Full example and more details can be found in [duetector_echocollector](./duetector_echocollector/)

## 1 Write a Collector

Here we write the echo Collector and set it to not `disabled` by defaylt.

```python
from typing import Optional, Dict, Any
from duetector.collectors import Collector
from duetector.collectors.models import Tracking

class EchoCollector(Collector):
    default_config = {
        "disabled": False,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    def _emit(self, t: Tracking):
        print(t)

    def summary(self) -> Dict:
        return {}


```

## 2 Register the Collector

```python
from duetector.extension.collector import hookimpl

@hookimpl
def init_collector(config):
    return EchoCollector(config)

```

## 3 Turning the Collector into a package

Here we use `pyproject.toml` as the configuration file.

```toml
# Build with hatch, you can use any build tool you like.
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "duetector-echocollector"

dependencies = ["duetector"]
dynamic = ["version"]

# This is the entry point for the CollectorManager to find the Collector.
[project.entry-points."duetector.collector"]
echocollector= "duetector_echocollector.echo"

[tool.hatch.version]
path = "duetector_echocollector/__init__.py"

```

## 4 Verification

Simply run the following code to verify the Collector is registered.

```python
from duetector.manager import CollectorManager
from duetector_echocollector.echo import EchoCollector


assert EchoCollector in (type(c) for c in CollectorManager().init())
```

## 5 Configuration

In `config.toml` you can set the Collector to be disabled.

```toml
[collector.EchoCollector]
disabled = true
```

In code, you can use `self.config.{config}` for any configuration. If the configuration is not set, it will use the default value in `self.default_config` or `None`.

Example:

Config the `EchoCollector` to pretty print the tracking data.

```toml
[collector.EchoCollector]
pretty = true
```

In code:

```python
class EchoCollector(Collector):
    default_config = {
        "disabled": False,
        "pretty": False,
    }

    def _emit(self, t: Tracking):
        if self.config.pretty:
            # Use pretty print
            self.pretty_print(t)
        else:
            print(t)
```
