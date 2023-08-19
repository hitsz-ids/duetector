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
        summary = {}
        for tracer, trackings in self._trackings.items():
            s = {}
            for tracking in trackings:
                if tracking.fname:
                    pid_tracking = s.setdefault(
                        f"{tracking.uid}:{tracking.gid} | [{tracking.pid}] {tracking.comm} | {tracking.cwd}",
                        dict(),
                    )
                    pid_tracking.setdefault(tracking.fname, 0)
                    pid_tracking[tracking.fname] += 1
                    if tracking.timestamp:
                        pid_tracking["last_updated"] = max(
                            pid_tracking.get("last_updated", 0), tracking.timestamp
                        )

            summary[tracer] = s

        return summary


@hookimpl
def init_collector(config):
    def _():
        return MemoryCollector(config)

    return _
