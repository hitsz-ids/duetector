import platform
from collections import deque
from typing import Any, Dict, Iterable, NamedTuple, Optional

from duetector.config import Configuable
from duetector.extension.collector import hookimpl

from .models import Tracking


class Collector(Configuable):
    default_config = {
        "disabled": False,
        "id": platform.node(),
    }

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled

    @property
    def id(self) -> str:
        # ID for current collector
        return self.config.id

    def emit(self, tracer, data: NamedTuple):
        if self.disabled:
            return
        self._emit(Tracking.from_namedtuple(tracer, data))

    def _emit(self, t: Tracking):
        raise NotImplementedError

    def summary(self) -> Dict:
        raise NotImplementedError


class DequeCollector(Collector):
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
        self._trackings: Dict[str, Iterable[Tracking]] = {}

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
