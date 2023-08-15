# TODO: This is a hack to get around the fact that we can't import BPF in tests

from collections import namedtuple

from duetector.tracers.base import Tracer


class DummyBPF:
    def __init__(self, text=None):
        pass

    def attach_dummy(self, **kwargs):
        pass


class DummyTracer(Tracer):
    # Fake a tracer that does nothing for testing purposes
    attach_type: str
    attatch_args: str
    poll_fn: str
    prog: str
    data_t: namedtuple

    @classmethod
    def attach(cls, bpf: DummyBPF):
        attatcher = getattr(bpf, f"attach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def add_callback(cls, bpf: DummyBPF, callback):
        def _(cpu, data, size):
            event = bpf["events"].event(data)
            return callback(cls._convert_data(event))

        bpf["events"].open_perf_buffer(_)

    @classmethod
    def get_poller(cls, bpf: DummyBPF):
        poller = getattr(bpf, cls.poll_fn)
        if not poller:
            raise
        return poller
