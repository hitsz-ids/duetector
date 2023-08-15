from typing import Any, List

from duetector.tracers.base import Tracer


class Monitor:
    bpf: Any
    traces: List[Tracer]
