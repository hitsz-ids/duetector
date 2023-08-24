from typing import Any, Dict, List, Optional

from duetector.collectors.base import Collector
from duetector.config import Configuable
from duetector.filters.base import Filter
from duetector.tracers.base import Tracer


class Monitor(Configuable):
    """
    A base class for all monitors

    A monitor is a collection of tracers, filters and collectors,
    record host and tracer, provide a way to poll data
    """

    tracers: List[Tracer]
    filters: List[Filter]
    collectors: List[Collector]

    config_scope = "monitor"

    default_config = {"disabled": False}

    @property
    def disabled(self):
        return self.config.disabled

    def init(self):
        raise NotImplementedError

    def poll_all(self):
        for tracer in self.tracers:
            self.poll(tracer)

    def poll(self, tracer: Tracer):
        raise NotImplementedError

    def summary(self) -> Dict:
        return {collector.__class__.__name__: collector.summary() for collector in self.collectors}
