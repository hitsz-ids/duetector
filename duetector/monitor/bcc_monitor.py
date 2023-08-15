from duetector.bcc import BPF, testing_mode
from duetector.monitor.base import Monitor
from duetector.tracers import OpenTracer


class BccMonitor(Monitor):
    def __init__(self):
        if testing_mode:
            from duetector.tracers.dummy import DummyTracer

            self.tracers = [DummyTracer]
        else:
            self.tracers = [OpenTracer]

        self.bpf = self._init_bpf()

    def _init_bpf(self) -> BPF:
        # TODO: Merge all tracers into one BPF program

        return BPF()
