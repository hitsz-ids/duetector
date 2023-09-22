from duetector.tracers.base import SubprocessTracer


class DummySpTracer(SubprocessTracer):
    default_config = {
        **SubprocessTracer.default_config,
        "disabled": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
