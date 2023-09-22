from typing import Any, Callable, Dict, List, Optional

from duetector.collectors.base import Collector
from duetector.log import logger
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors import Monitor
from duetector.tracers.base import SubprocessTracer


class SubprocessHost:
    pass


class SubprocessMonitor(Monitor):
    default_config = {
        **Monitor.default_config,
        "auto_init": True,
        "timeout": 5,
    }

    @property
    def auto_init(self):
        """
        Auto init tracers when init monitor.
        """
        return self.config.auto_init

    @property
    def timeout(self):
        """
        Timeout for shell command.
        """
        return int(self.config.timeout)

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config, *args, **kwargs)
        if self.disabled:
            logger.info("SubprocessMonitor disabled")
            self.tracers = []
            self.filters = []
            self.collectors = []
            return

        self.tracers: List[SubprocessTracer] = TracerManager(config).init(tracer_type=SubprocessTracer)  # type: ignore
        self.filters: List[Callable] = FilterManager(config).init()
        self.collectors: List[Collector] = CollectorManager(config).init()

        if self.auto_init:
            self.init()

    def init():
        pass
