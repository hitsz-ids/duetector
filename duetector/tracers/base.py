from collections import namedtuple
from typing import Callable, Dict

from duetector.exceptions import TracerError


class Tracer:
    pass


class BccTracer:
    attach_type: str
    attatch_args: Dict[str, str] = {}
    poll_fn: str
    poll_args: Dict[str, str] = {}
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
        if not cls.attach_type:
            # No need to attach, in this case, function name indicates
            # More: https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md
            return
        attatcher = getattr(bpf, f"attach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def detach(cls, bpf):
        if not cls.attach_type:
            # Means prog is not attached by python's BPF.attatch_()
            # So user should detach it manually
            raise TracerError("Unable to detach, no attach type specified")
        attatcher = getattr(bpf, f"detach_{cls.attach_type}")
        return attatcher(**cls.attatch_args)

    @classmethod
    def get_poller(cls, bpf) -> Callable:
        if not cls.poll_fn:
            # Not support poll

            def _(*args, **kwargs):
                pass

            # Prevent AttributeError
            return _

        poller = getattr(bpf, cls.poll_fn)
        if not poller:
            raise TracerError(f"{cls.poll_fn} function not found in BPF")
        return poller

    @classmethod
    def add_callback(cls, bpf, callback: Callable[[namedtuple], None]):
        raise NotImplementedError("add_callback not implemented")
