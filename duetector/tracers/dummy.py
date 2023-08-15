# TODO: This is a hack to get around the fact that we can't import BPF in tests

from collections import namedtuple

from duetector.bcc import BPF, testing_mode
from duetector.tracers.base import Tracer


class DummyTracer(Tracer):
    # Fake a tracer that does nothing for testing purposes
    attach_type: str
    attatch_args: str
    poll_fn: str
    prog: str
    data_t: namedtuple

    @classmethod
    def attach(cls, bpf: BPF):
        attatcher = getattr(bpf, f"attach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def add_callback(cls, bpf: BPF, callback):
        def _(cpu, data, size):
            event = bpf["events"].event(data)
            return callback(cls._convert_data(event))

        bpf["events"].open_perf_buffer(_)

    @classmethod
    def get_poller(cls, bpf: BPF):
        poller = getattr(bpf, cls.poll_fn)
        if not poller:
            raise
        return poller
