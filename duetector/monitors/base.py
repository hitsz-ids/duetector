from typing import Any, Dict, List, Optional

from duetector.collectors.base import Collector
from duetector.config import Configuable
from duetector.filters.base import Filter
from duetector.tracers.base import Tracer


class Monitor(Configuable):
    traces: List[Tracer]
    filters: List[Filter]
    collectors: List[Collector]

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled
