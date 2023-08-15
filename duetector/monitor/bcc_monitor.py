from duetector.monitor.base import Monitor
from duetector.tracers import OpenTracer


class BccMonitor(Monitor):
    def __init__(self):
        self.tracers = [OpenTracer]
        self.bpf = self._init_bpf()

    def _init_bpf(self):
        from bcc import BPF

        # TODO: Merge all tracers into one BPF program
        return BPF()
