from typing import Any, Callable, Dict, List

from duetector.collectors import Collector
from duetector.filters import Filter
from duetector.monitors.base import Monitor
from duetector.tracers import BccTracer
from duetector.tracers.open import OpenTracer


class BccMonitor(Monitor):
    def __init__(self):
        # TODO: Add more Tracer and support plugin system
        # Something like this:
        #  # Get all tracers from TracerManager
        #  self.tracers.append(TracerManager().get_tracers())
        self.tracers: List[BccTracer] = [OpenTracer]

        # TODO: Implement filters and plugin system
        # Something like this:
        #  self.filters = FilterManager().get_filters()
        self.filters: Dict[Callable] = [Filter()]

        # TODO: Implement plugin system
        self.collectors: Dict[Collector] = [Collector()]

        self.bpf_tracers: Dict[Any, BccTracer] = {}
        self._init_bpf()

    def _init_bpf(self):
        # Prevrent ImportError for CI testing without bcc
        from bcc import BPF  # noqa

        for tracer in self.tracers:
            try:
                bpf = BPF(text=tracer.prog)
            except Exception:
                # Compiler error
                # TODO: Add logger
                continue
            self.bpf_tracers[tracer] = bpf
            tracer.attach(bpf)
            self._add_filters_callback(tracer)

    def _add_filters_callback(self, tracer):
        def _(data):
            for filter in self.filters:
                data = filter(data)
            for collector in self.collectors:
                collector.emit(data)

        tracer.add_callback(self.bpf_tracers[tracer], _)

    def poll_all(self):
        for tracer in self.tracers:
            self.poll(tracer)

    def poll(self, tracer: BccTracer):
        tracer.get_poller(self.bpf_tracers[tracer])(**tracer.poll_args)


if __name__ == "__main__":
    m = BccMonitor()
    while True:
        try:
            m.poll_all()

        except KeyboardInterrupt:
            exit()
