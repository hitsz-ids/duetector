from collections import namedtuple


class Tracer:
    attach_type: str
    attatch_args: str
    poll_fn: str
    prog: str
    data_t: namedtuple

    @classmethod
    def _convert_data(cls, data) -> namedtuple:
        args = {}
        for k in cls.data_t._fields:
            v = getattr(data, k)
            if isinstance(v, bytes):
                v = v.decode("utf-8")

            args[k] = v

        return cls.data_t(**args)

    @classmethod
    def attach(cls, bpf):
        attatcher = getattr(bpf, f"attach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def add_callback(cls, bpf, callback):
        def _(cpu, data, size):
            event = bpf["events"].event(data)
            return callback(cls._convert_data(event))

        bpf["events"].open_perf_buffer(_)

    @classmethod
    def get_poller(cls, bpf):
        poller = getattr(bpf, cls.poll_fn)
        if not poller:
            raise
        return poller
