from collections import namedtuple
from threading import Lock
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

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

    attatch_type: str attatch type for bcc.BPF, e.g. kprobe, kretprobe, etc.
    attatch_args: Dict[str, str]  args for attatch function
    many_attatchs: List[Tuple[str, Dict[str, str]]] list of attatch function name and args
    poll_fn: str  poll function name in bcc.BPF
    poll_args: Dict[str, str]  args for poll function
    prog: str  bpf program
    data_t: NamedTuple  data type for this tracer

    For simple tracers, you can just set `attach_type`, `attatch_args` to attatch to bcc.BPF
    equal to `bcc.BPF(prog).attatch_{attatch_type}(**attatch_args)`

    For those tracers need to attatch multiple times, you can set `many_attatchs` to attatch multiple times

    set_callback should attatch callback to bpf, translate raw data to data_t then call the callback
    # FIXME: Maybe it's hard for using? Maybe we should use a more simple way to implement this?
    """

    default_config = {
        **Tracer.default_config,
    }

    attach_type: Optional[str] = None
    attatch_args: Dict[str, str] = {}
    many_attatchs: List[Tuple[str, Dict[str, str]]] = []
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
            elif k == "saddr" or k == "daddr":
                dq = b""
                for i in range(0, 4):
                    dq = dq + str(v & 0xFF).encode()
                    if i != 3:
                        dq = dq + b"."
                    v = v >> 8
                v = dq

            args[k] = v

        return self.data_t(**args)  # type: ignore

    def _attatch(self, host, attatch_type, attatch_args):
        if not attatch_type:
            return
        attatcher = getattr(host, f"attach_{attatch_type}")
        # Prevent AttributeError
        attatch_args = attatch_args or {}
        return attatcher(**attatch_args)

    def attach(self, host):
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        attatch_list = [*self.many_attatchs, (self.attach_type, self.attatch_args)]

        for attatch_type, attatch_args in attatch_list:
            self._attatch(host, attatch_type, attatch_args)

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
