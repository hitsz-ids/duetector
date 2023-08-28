from collections import namedtuple
from threading import Lock
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union

from duetector.config import Config, Configuable
from duetector.exceptions import TracerError, TreacerDisabledError


class Tracer(Configuable):
    """
    A base class for all tracers

    Subclass should implement attach, detach, get_poller and set_callback
    `data_t` is a NamedTuple, which is used to convert raw data to a NamedTuple
    """

    data_t: NamedTuple
    default_config = {
        "disabled": False,
    }

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

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        # attatch callback to host
        raise NotImplementedError("set_callback not implemented")


class BccTracer(Tracer):
    """
    A Tracer use bcc.BPF host

    attatch_type: str  attatch type for bcc.BPF, e.g. kprobe, kretprobe, etc.
    attatch_args: Dict[str, str]  args for attatch function
    poll_fn: str  poll function name in bcc.BPF
    poll_args: Dict[str, str]  args for poll function
    prog: str  bpf program
    data_t: NamedTuple  data type for this tracer

    set_callback should attatch callback to bpf, translate raw data to data_t then call the callback
    # FIXME: Maybe it's hard for using? Maybe we should use a more simple way to implement this?
    """

    default_config = {
        **Tracer.default_config,
    }

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

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        raise NotImplementedError("set_callback not implemented")


class ShellTracer(Tracer):
    comm = List[str]
    data_t = namedtuple("ShellOutput", ["output"])

    _cache: Optional[Any] = None
    default_config = {"disabled": False, "enable_cache": True}

    def __init__(self, config: Optional[Union[Config, Dict[str, Any]]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.mutex = Lock()

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def enable_cache(self):
        return self.config.enable_cache

    @property
    def disabled(self):
        return self.config.disabled

    def set_cache(self, cache):
        with self.mutex:
            self._cache = cache

    def get_cache(self):
        return self._cache

    def attach(self, host):
        host.attach(self)

    def detach(self, host):
        host.detach(self)

    def get_poller(self, host) -> Callable:
        return host.get_poller(self)

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        host.set_callback(self, callback)
