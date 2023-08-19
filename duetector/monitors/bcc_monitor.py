from typing import Any, Callable, Dict, List, Type

from duetector.collectors.base import Collector, MemoryCollector
from duetector.extension.collector.manager import CollectorManager
from duetector.extension.filter.manager import FilterManager
from duetector.extension.tracer.manager import TracerManager
from duetector.filters import Filter
from duetector.monitors.base import Monitor
from duetector.tracers import BccTracer


class BccMonitor(Monitor):
    def __init__(self, config=None):
        # TODO: Dependency injection for config
        super().__init__(config=config)

        self.tracers: List[BccTracer] = TracerManager(config).init()
        self.filters: List[Callable] = FilterManager(config).init()
        self.collectors: List[Collector] = CollectorManager(config).init()

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
            self._add_callback(tracer)

    def _add_callback(self, tracer):
        def _(data):
            for filter in self.filters:
                data = filter(data)
                if not data:
                    return
            for collector in self.collectors:
                collector.emit(getattr(tracer, "name", tracer), data)

        tracer.add_callback(self.bpf_tracers[tracer], _)

    def poll_all(self):
        for tracer in self.tracers:
            self.poll(tracer)

    def poll(self, tracer: BccTracer):
        tracer.get_poller(self.bpf_tracers[tracer])(**tracer.poll_args)

    def summary(self):
        return {collector.__class__.__name__: collector.summary() for collector in self.collectors}


if __name__ == "__main__":
    m = BccMonitor()
    while True:
        try:
            m.poll_all()
            print(m.summary())
        except KeyboardInterrupt:
            exit()
