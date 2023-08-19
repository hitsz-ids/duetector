from collections import deque
from typing import Dict, Iterable, NamedTuple

from duetector.extension.collector import hookimpl

from .models import Tracking


class Collector:
    def __init__(self, config=None):
        self.config = config

    def emit(self, tracer, data: NamedTuple):
        self._emit(Tracking.from_namedtuple(tracer, data))

    def _emit(self, t: Tracking):
        raise NotImplementedError

    def summary(self) -> Dict:
        raise NotImplementedError


class MemoryCollector(Collector):
    def __init__(self, config=None):
        super().__init__(config=config)
        self._trackings: Dict[str, Iterable[Tracking]] = {}
        self.maxlen = 1024

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
    return MemoryCollector(config)
