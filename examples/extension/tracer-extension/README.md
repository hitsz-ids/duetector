In this example we will write a BccTracer only print log when syscall `clone` is called.

Full example and more details can be found in [duetector_logtracer](./duetector_logtracer/)

## 1 Write a Tracer

Here we write the echo Tracer and set it to not `disabled` by defaylt.

```python
from collections import namedtuple
from typing import Callable, NamedTuple

from duetector.tracers.base import BccTracer


class LogTracer(BccTracer):
    attach_type = "kprobe"
    attatch_args = {"fn_name": "hello", "event": "__x64_sys_clone"}
    poll_fn = None
    poll_args = {}
    data_t = namedtuple(
        "FieldTracking", ["pid", "uid", "gid", "comm", "fname", "timestamp"]
    )

    prog = """
    int hello(void *ctx) {
        bpf_trace_printk("Hello, World!\\n");
        return 0;
    }
    """

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        # No need to collect data
        return
```

## 2 Register the Tracer

```python
from duetector.extension.tracer import hookimpl

@hookimpl
def init_tracer(config):
    return LogTracer(config)
```

## 3 Turning the Tracer into a package

Here we use `pyproject.toml` as the configuration file.

```toml
# Build with hatch, you can use any build tool you like.
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "duetector-logtracer"

dependencies = ["duetector"]
dynamic = ["version"]

# This is the entry point for the TracerManager to find the Tracer.
[project.entry-points."duetector.tracer"]
logtracer = "duetector_logtracer.log"

[tool.hatch.version]
path = "duetector_logtracer/__init__.py"
```

## 4 Verification

Simply run the following code to verify the Tracer is registered.

```python
from duetector.manager import TracerManager
from duetector.tracer import BccTracer

from duetector_logtracer.log import LogTracer


assert LogTracer in (type(c) for c in TracerManager().init(BccTracer))
```

## 5 Configuration

In `config.toml` you can set the Tracer to be disabled.

```toml
[Tracer.LogTracer]
disabled = true
```

In code, you can use `self.config.{config}` for any configuration. If the configuration is not set, it will use the default value in `self.default_config` or `None`.
