from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional

from duetector.collectors.base import Collector
from duetector.log import logger
from duetector.managers import CollectorManager, FilterManager, TracerManager
from duetector.monitors.base import Monitor
from duetector.tracers import BccTracer


class BccMonitor(Monitor):
    """
    A monitor use bcc.BPF host

    Config:
        - auto_init: Init tracers on init
    """

    config_scope = "monitor.bcc"
    default_config = {
        **Monitor.default_config,
        "auto_init": True,
        "continue_on_exception": True,
    }

    @property
    def continue_on_exception(self):
        return self.config.continue_on_exception

    @property
    def auto_init(self):
        return self.config.auto_init

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config)
        if self.disabled:
            logger.info("BccMonitor disabled")
            self.tracers = []
            self.filters = []
            self.collectors = []
            return

        self.tracers: List[BccTracer] = TracerManager(config).init(tracer_type=BccTracer)  # type: ignore
        self.filters: List[Callable] = FilterManager(config).init()
        self.collectors: List[Collector] = CollectorManager(config).init()

        self.bpf_tracers: Dict[Any, BccTracer] = {}
        if self.auto_init:
            self.init()

    def init(self):
        # Prevrent ImportError for CI testing without bcc
        from bcc import BPF  # noqa

        for tracer in self.tracers:
            try:
                bpf = BPF(text=tracer.prog)
            except Exception as e:
                logger.error(f"Failed to compile {tracer.__class__.__name__}")
                logger.exception(e)
                if self.continue_on_exception:
                    continue
                else:
                    raise e
            tracer.attach(bpf)
            self._set_callback(bpf, tracer)
            self.bpf_tracers[tracer] = bpf
            logger.info(f"Tracer {tracer.__class__.__name__} attached")

    def _set_callback(self, host, tracer):
        def _(data):
            for filter in self.filters:
                data = filter(data)
                if not data:
                    return
            for collector in self.collectors:
                collector.emit(tracer, data)

        tracer.set_callback(host, _)

    def poll(self, tracer: BccTracer):  # type: ignore
        tracer.get_poller(self.bpf_tracers[tracer])(**tracer.poll_args)

    def summary(self):
        return {collector.__class__.__name__: collector.summary() for collector in self.collectors}


if __name__ == "__main__":
    m = BccMonitor()
    print(m)
    r = None
    while True:
        try:
            m.poll_all()
            pass
        except KeyboardInterrupt:
            print(m.summary())
            exit()
