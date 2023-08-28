import platform
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Deque, Dict, Iterable, NamedTuple, Optional, Union

from duetector.config import Config, Configuable
from duetector.extension.collector import hookimpl

from .models import Tracking


class Collector(Configuable):
    """
    Base class for all collectors
    """

    default_config = {
        "disabled": False,
        "statis_id": "",
        "backend_args": {
            "max_workers": 10,
        },
    }
    _backend_imp = ThreadPoolExecutor

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self._backend = self._backend_imp(**self.backend_args.config_dict)

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled

    @property
    def id(self) -> str:
        # ID for current collector
        # If not set, use hostname
        return self.config.statis_id or platform.node()

    @property
    def backend_args(self):
        return self.config.backend_args

    def emit(self, tracer, data: NamedTuple):
        if self.disabled:
            return
        self._backend.submit(self._emit, Tracking.from_namedtuple(tracer, data))

    def _emit(self, t: Tracking):
        raise NotImplementedError

    def summary(self) -> Dict:
        raise NotImplementedError

    def shutdown(self):
        self._backend.shutdown()


class DequeCollector(Collector):
    """
    A simple collector using deque, disabled by default

    Config:
        - maxlen: Max length of deque
    """

    default_config = {
        **Collector.default_config,
        "disabled": True,
        "maxlen": 1024,
    }

    @property
    def maxlen(self):
        return self.config.maxlen

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self._trackings: Dict[str, Deque[Tracking]] = {}

    def _emit(self, t: Tracking):
        self._trackings.setdefault(t.tracer, deque(maxlen=self.maxlen))
        self._trackings[t.tracer].append(t)

    def summary(self) -> Dict:
        return {
            tracer: {
                "count": len(trackings),
                "first": trackings[0].timestamp,
                "last": trackings[-1].timestamp,
                "most_recent": trackings[-1].model_dump(),
            }
            for tracer, trackings in self._trackings.items()
        }


@hookimpl
def init_collector(config):
    return DequeCollector(config)
