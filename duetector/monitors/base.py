from concurrent.futures import ThreadPoolExecutor
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

    default_config = {
        "disabled": False,
        "backend_args": {
            "max_workers": 10,
        },
    }

    _backend_imp = ThreadPoolExecutor

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config)
        self._backend = self._backend_imp(**self.backend_args.config_dict)

    @property
    def disabled(self):
        return self.config.disabled

    @property
    def backend_args(self):
        return self.config.backend_args

    def poll_all(self):
        self._backend.map(self.poll, self.tracers)

    def poll(self, tracer: Tracer):
        raise NotImplementedError

    def summary(self) -> Dict:
        return {collector.__class__.__name__: collector.summary() for collector in self.collectors}

    def shutdown(self):
        self._backend.shutdown()
        for c in self.collectors:
            c.shutdown()
