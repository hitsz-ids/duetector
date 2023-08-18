# TODO

import pytest

from duetector.collectors import Collector
from duetector.filters import Filter
from duetector.monitors.bcc_monitor import BccMonitor
from duetector.tracers.dummy import DummyBPF, DummyTracer


class MockMonitor(BccMonitor):
    def __init__(self):
        self.tracers = [DummyTracer]
        self.filters = [Filter()]
        self.collectors = [Collector()]

        self.bpf_tracers = {}
        self._init_bpf()

    def _init_bpf(self):
        for tracer in self.tracers:
            try:
                bpf = DummyBPF(text=tracer.prog)
            except Exception:
                # Compiler error
                # TODO: Add logger
                continue
            self.bpf_tracers[tracer] = bpf
            tracer.attach(bpf)
            self._add_callback(tracer)


@pytest.fixture
def bcc_monitor():
    yield MockMonitor()


def test_bcc_monitor():
    pass
