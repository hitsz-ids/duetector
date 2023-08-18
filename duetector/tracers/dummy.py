from collections import namedtuple

from duetector.tracers.base import Tracer


class DummyBPF:
    def __init__(self, text=None):
        self.callback

    def attach_dummy(self, **kwargs):
        pass

    def poll_dummy(self, **kwargs):
        self.callback()

    def add_callback(self, func):
        self.callback = func()


class DummyTracer(Tracer):
    # Fake a tracer that does nothing for testing purposes
    attach_type = "dummy"
    poll_fn = "poll_dummy"
    prog = "This is nor a prog to run"
    data_t = namedtuple("DummyTracking", ["pid", "uid", "gid", "comm", "fname"])

    @classmethod
    def attach(cls, bpf: DummyBPF):
        attatcher = getattr(bpf, f"attach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def add_callback(cls, bpf: DummyBPF, callback):
        def _(cpu, data, size):
            data = cls.data_t()
            return callback(data)

        bpf.add_callback(_)

    @classmethod
    def get_poller(cls, bpf: DummyBPF):
        poller = getattr(bpf, cls.poll_fn)
        if not poller:
            raise
        return poller
