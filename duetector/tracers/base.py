from collections import namedtuple
from typing import Callable, Dict, NamedTuple

from duetector.exceptions import TracerError


class Tracer:
    data_t: NamedTuple

    def __init__(self, config=None):
        # TODO: Dependency injection for config
        self.config = config

    def attach(self, manager):
        raise NotImplementedError("attach not implemented")

    def detach(self, manager):
        raise NotImplementedError("detach not implemented")

    def get_poller(self, manager) -> Callable:
        raise NotImplementedError("get_poller not implemented")

    def add_callback(self, manager, callback: Callable[[NamedTuple], None]):
        raise NotImplementedError("add_callback not implemented")


class BccTracer(Tracer):
    attach_type: str
    attatch_args: Dict[str, str] = {}
    poll_fn: str
    poll_args: Dict[str, str] = {}
    prog: str
    data_t: NamedTuple

    def _convert_data(self, data) -> NamedTuple:
        args = {}
        for k in self.data_t._fields:  # type: ignore
            v = getattr(data, k)
            if isinstance(v, bytes):
                v = v.decode("utf-8")

            args[k] = v

        return self.data_t(**args)  # type: ignore

    def attach(self, bpf):
        if not self.attach_type:
            # No need to attach, in this case, function name indicates
            # More: https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md
            return
        attatcher = getattr(bpf, f"attach_{self.attach_type}")
        return attatcher(**self.attatch_args)

    def detach(self, bpf):
        if not self.attach_type:
            # Means prog is not attached by python's BPF.attatch_()
            # So user should detach it manually
            raise TracerError("Unable to detach, no attach type specified")
        attatcher = getattr(bpf, f"detach_{self.attach_type}")
        return attatcher(**self.attatch_args)

    def get_poller(self, bpf) -> Callable:
        if not self.poll_fn:
            # Not support poll

            def _(*args, **kwargs):
                pass

            # Prevent AttributeError
            return _

        poller = getattr(bpf, self.poll_fn)
        if not poller:
            raise TracerError(f"{self.poll_fn} function not found in BPF")
        return poller

    def add_callback(self, bpf, callback: Callable[[NamedTuple], None]):
        raise NotImplementedError("add_callback not implemented")
