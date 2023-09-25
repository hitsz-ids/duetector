from pathlib import Path

from duetector.tracers.base import SubprocessTracer

_HERE = Path(__file__).parent


class DummySpTracer(SubprocessTracer):
    default_config = {
        **SubprocessTracer.default_config,
        "disabled": True,
    }

    comm = ["python3", (_HERE / "dummy_process.py").as_posix()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
