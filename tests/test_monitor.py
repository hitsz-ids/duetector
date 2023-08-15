# TODO

import pytest

from duetector.monitor.bcc_monitor import BccMonitor
from duetector.tracers.dummy import DummyBPF, DummyTracer


class DummyMonitor(BccMonitor):
    def __init__(self):
        self.tracers = [DummyTracer()]
        self.bpf = DummyBPF()


@pytest.fixture
def bcc_monitor():
    yield DummyMonitor()


def test_bcc_monitor():
    pass
