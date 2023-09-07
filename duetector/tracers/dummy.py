from collections import namedtuple
from typing import Callable

from duetector.tracers.base import BccTracer


class DummyBPF:
    def __init__(self, text=None):
        self.text = text

    def attach_dummy(self, **kwargs):
        pass

    def poll_dummy(self, **kwargs):
        self.callback()

    def set_callback(self, func):
        self.callback = func


class DummyTracer(BccTracer):
    """
    Fake a tracer that does nothing for testing.
    """

    attach_type = "dummy"
    poll_fn = "poll_dummy"
    prog = "This is not a runnable program"
    data_t = namedtuple(
        "DummyTracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"]
    )

    def attach(self, host: DummyBPF):
        super().attach(host)

    def detach(self, host: DummyBPF):
        super().detach(host)

    @classmethod
    def get_dummy_data(cls):
        return cls.data_t(
            pid=9999,
            uid=9999,
            gid=9999,
            comm="dummy",
            fname="dummy.file",
            timestamp=13205215231927,
            custom="dummy-xargs",
        )

    def set_callback(self, bpf: DummyBPF, callback):
        def _():
            return callback(self.get_dummy_data())

        bpf.set_callback(_)

    def get_poller(self, host: DummyBPF) -> Callable:
        return super().get_poller(host)
