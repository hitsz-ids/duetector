from typing import List

from duetector.collectors.base import Collector
from duetector.filters.base import Filter
from duetector.tracers.base import Tracer


class Monitor:
    traces: List[Tracer]
    filters: List[Filter]
    collectors: List[Collector]

    def __init__(self, config=None):
        # TODO: Dependency injection for config
        self.config = config
