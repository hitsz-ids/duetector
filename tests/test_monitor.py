# TODO

import pytest

from duetector.manager import CollectorManager, FilterManager, TracerManager
from duetector.monitors.bcc_monitor import BccMonitor
from duetector.tracers.dummy import DummyBPF, DummyTracer


class MockMonitor(BccMonitor):
    def __init__(self, config=None):
        self.config = config

        self.tracers = [DummyTracer(config)]
        self.filters = FilterManager(config).init()
        self.collectors = CollectorManager(config).init()

        self.bpf_tracers = {}
        self._init_bpf()

    def _init_bpf(self):
        for tracer in self.tracers:
            bpf = DummyBPF(text=tracer.prog)
            self.bpf_tracers[tracer] = bpf
            tracer.attach(bpf)
            self._add_callback(tracer)


@pytest.fixture
def bcc_monitor(config):
    yield MockMonitor(config)


def test_bcc_monitor(bcc_monitor: MockMonitor):
    bcc_monitor.poll_all()
    print(bcc_monitor.summary())


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
