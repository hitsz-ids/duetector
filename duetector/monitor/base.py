from typing import List

from duetector.bcc import BPF
from duetector.tracers.base import Tracer


class Monitor:
    bpf: BPF
    traces: List[Tracer]
