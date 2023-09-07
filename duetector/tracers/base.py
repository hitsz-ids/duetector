from collections import namedtuple
from threading import Lock
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from duetector.config import Config, Configuable
from duetector.exceptions import TracerError, TreacerDisabledError


class Tracer(Configuable):
    """
    A base class for all tracers.

    As a reverse dependency for host,
    subclass should implement ``attach``, ``detach``, ``get_poller`` and ``set_callback``.
    This allow tracer to decide how to attach to host, how to detach from host.

    ``data_t`` is a NamedTuple, which is used to convert raw data to a ``NamedTuple``.

    Default scope for config is ``Tracer.__class__.__name__``.
    """

    data_t: NamedTuple
    """
    Data type for this tracer.
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for this tracer.
    """

    @property
    def config_scope(self):
        """
        Config scope for this tracer.
        """
        return self.__class__.__name__

    @property
    def disabled(self):
        """
        If this tracer is disabled.
        """
        return self.config.disabled

    def attach(self, host):
        """
        Attach this tracer to host.
        """
        raise NotImplementedError("attach not implemented")

    def detach(self, host):
        """
        Detach this tracer from host.
        """
        raise NotImplementedError("detach not implemented")

    def get_poller(self, host) -> Callable:
        """
        Get a poller function from host.
        """
        raise NotImplementedError("get_poller not implemented")

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        """
        Set a callback function to host.
        """
        raise NotImplementedError("set_callback not implemented")


class BccTracer(Tracer):
    """
    A Tracer use ``bcc.BPF`` as a host

    For simple tracers, you can just set ``attach_type``, ``attatch_args`` to attatch to ``bcc.BPF``.
    Equal to `bcc.BPF(prog).attatch_{attatch_type}(**attatch_args)`

    For those tracers need to attatch multiple times, set ``many_attatchs`` to attatch multiple times.

    ``set_callback`` should attatch ``callback`` to ``bpf``, translate raw data to ``data_t`` then call the ``callback``

    FIXME:
        - Maybe it's hard for using? Maybe we should use a more simple way to implement this?
    """

    default_config = {
        **Tracer.default_config,
    }
    """
    Default config for this tracer.
    """

    attach_type: Optional[str] = None
    """
    Attatch type for ``bcc.BPF``, called as ``BPF.attatch_{attach_type}``,
    """

    attatch_args: Dict[str, str] = {}
    """
    Args for attatch function.
    """

    many_attatchs: List[Tuple[str, Dict[str, str]]] = []
    """
    List of attatch function name and args.
    ``attatch_type``, ``attatch_args`` will merge to this list.
    """

    poll_fn: str
    """
    Poll function name in ``bcc.BPF``
    """

    poll_args: Dict[str, str] = {}
    """
    Args for poll function.
    Remenber to set ``timeout`` for poll function in ``poll_args`` if needed,
    """

    prog: str
    """
    bpf program
    """

    def _convert_data(self, data) -> NamedTuple:
        """
        Convert raw data to ``data_t``.
        """
        args = {}
        for k in self.data_t._fields:  # type: ignore
            v = getattr(data, k)
            if isinstance(v, bytes):
                v = v.decode("utf-8")

            args[k] = v

        return self.data_t(**args)  # type: ignore

    def _attatch(self, host, attatch_type, attatch_args):
        """
        Wrapper for ``bcc.BPF.attatch_{attatch_type}``.
        """
        if not attatch_type:
            return
        attatcher = getattr(host, f"attach_{attatch_type}")
        # Prevent AttributeError
        attatch_args = attatch_args or {}
        return attatcher(**attatch_args)

    def attach(self, host):
        """
        Attatch to host.

        Merge ``attatch_type``, ``attatch_args`` to ``many_attatchs`` then attatch.
        """
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        attatch_list = [*self.many_attatchs, (self.attach_type, self.attatch_args)]

        for attatch_type, attatch_args in attatch_list:
            self._attatch(host, attatch_type, attatch_args)

    def _detach(self, host, attatch_type, attatch_args):
        """
        Wrapper for ``bcc.BPF.detach_{attatch_type}``
        """
        if not attatch_type:
            return
        attatcher = getattr(host, f"detach_{attatch_type}")
        # Prevent AttributeError
        attatch_args = attatch_args or {}
        return attatcher(**attatch_args)

    def detach(self, host):
        """
        Detach from host.

        Merge ``attatch_type``, ``attatch_args`` to ``many_attatchs`` then detach.

        FIXME:
            - Maybe we should specify ``detach*`` for detaching?
        """
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        attatch_list = [*self.many_attatchs, (self.attach_type, self.attatch_args)]

        for attatch_type, attatch_args in attatch_list:
            self._detach(host, attatch_type, attatch_args)

    def get_poller(self, host) -> Callable:
        """
        Get poller function from host.
        """
        if self.disabled:
            raise TreacerDisabledError("Tracer is disabled")

        if not self.poll_fn:
            # Not support poll, prevent AttributeError, fake one

            def _(*args, **kwargs):
                pass

            return _

        poller = getattr(host, self.poll_fn)
        if not poller:
            raise TracerError(f"{self.poll_fn} function not found in BPF")
        return poller

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        """
        Set callback function to host.

        Should implemented by subclass.
        """
        raise NotImplementedError("set_callback not implemented")


class ShellTracer(Tracer):
    """
    A tracer use ``ShTracerHost`` as host.
    More detail on :doc:`ShellMonitor and ShTracerHost </monitors/sh>`.

    Output of shell command will be converted to ``data_t`` and cached by default.

    Attributes:
        comm (List[str]): shell command
        data_t (NamedTuple): data type for this tracer

    Special config:
        - enable_cache: If enable cache for this tracer.
                        Cache means the same output will not be converted and emited again.
    """

    comm = List[str]
    """
    shell command
    """
    data_t = namedtuple("ShellOutput", ["output"])
    """
    data type for this tracer
    """

    _cache: Optional[Any] = None
    """
    cache for this tracer
    """
    default_config = {**Tracer.default_config, "enable_cache": True}
    """
    Default config for this tracer.
    """

    def __init__(self, config: Optional[Union[Config, Dict[str, Any]]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.mutex = Lock()

    @property
    def enable_cache(self):
        """
        If enable cache for this tracer.
        """

        return self.config.enable_cache

    @property
    def disabled(self):
        return self.config.disabled

    def set_cache(self, cache):
        """
        Set cache for this tracer.
        """
        with self.mutex:
            self._cache = cache

    def get_cache(self):
        """
        Get cache for this tracer.
        """
        return self._cache

    def attach(self, host):
        """
        Attach to host.
        """
        host.attach(self)

    def detach(self, host):
        """
        Detach from host.
        """
        host.detach(self)

    def get_poller(self, host) -> Callable:
        """
        Get poller function from host.
        """
        return host.get_poller(self)

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        """
        Set callback function to host.
        """
        host.set_callback(self, callback)
