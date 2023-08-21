from collections import namedtuple
from typing import Any, Callable, Dict, NamedTuple, Optional

from duetector.config import Configuable
from duetector.exceptions import TracerError, TreacerDisabledError


class Tracer(Configuable):
    data_t: NamedTuple

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled

    def attach(self, host):
        raise NotImplementedError("attach not implemented")

    def detach(self, host):
        raise NotImplementedError("detach not implemented")

    def get_poller(self, host) -> Callable:
        raise NotImplementedError("get_poller not implemented")

    def add_callback(self, host, callback: Callable[[NamedTuple], None]):
        raise NotImplementedError("add_callback not implemented")


class BccTracer(Tracer):
    """
    host of BccTracer is bcc.BPF
    """

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

    def attach(self, host):
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        if not self.attach_type or self.disabled:
            # No need to attach, in this case, function name indicates
            # More: https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md
            return
        attatcher = getattr(host, f"attach_{self.attach_type}")
        return attatcher(**self.attatch_args)

    def detach(self, host):
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        if not self.attach_type:
            # Means prog is not attached by python's BPF.attatch_()
            # So user should detach it manually
            raise TracerError("Unable to detach, no attach type specified")
        attatcher = getattr(host, f"detach_{self.attach_type}")
        return attatcher(**self.attatch_args)

    def get_poller(self, host) -> Callable:
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        if not self.poll_fn:
            # Not support poll

            def _(*args, **kwargs):
                pass

            # Prevent AttributeError
            return _

        poller = getattr(host, self.poll_fn)
        if not poller:
            raise TracerError(f"{self.poll_fn} function not found in BPF")
        return poller

    def add_callback(self, host, callback: Callable[[NamedTuple], None]):
        raise NotImplementedError("add_callback not implemented")
