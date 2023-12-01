from __future__ import annotations

from collections import namedtuple

from duetector.injectors.base import Injector
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.injector import InjectorManager

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from duetector.collectors.base import Collector
from duetector.config import Configuable
from duetector.filters.base import Filter
from duetector.log import logger
from duetector.tools.poller import Poller
from duetector.tracers.base import Tracer


class Monitor(Configuable):
    """
    A base class for all monitors

    A monitor is a collection of tracers, filters and collectors,
    record host and tracer, provide a way to poll data
    """

    tracers: list[Tracer]
    """
    A list of tracers, should be initialized by ``TracerManager``
    """
    filters: list[Filter]
    """
    A list of filters, should be initialized by ``FilterManager``
    """
    collectors: list[Collector]
    """
    A list of collectors, should be initialized by ``CollectorManager``
    """
    injectors: list[Injector]
    """
    A list of collectors, should be initialized by ``InjectorManager``
    """

    config_scope = "monitor"
    """
    Config scope for monitor.
    """

    default_config = {
        "disabled": False,
        "backend_args": {
            "max_workers": 10,
        },
        "poller": {
            **Poller.default_config,
        },
    }
    """
    Default config for monitor.

    Two sub-configs are available:
        - backend_args: config for ``self._backend_imp``
        - poller: config for ``Poller``
    """

    _backend_imp = ThreadPoolExecutor
    """
    A backend implementation.
    """

    def __init__(self, config: dict[str, Any] | None = None, *args, **kwargs):
        super().__init__(config=config)
        self._backend = self._backend_imp(**self.backend_args._config_dict)
        self.poller = Poller(self.config._config_dict)

        if self.disabled:
            self.tracers = []
            self.filters = []
            self.collectors = []
            self.injectors = []
            return
        self.filters: list[Filter] = FilterManager(config).init()
        self.collectors: list[Collector] = CollectorManager(config).init()
        self.injectors: list[Injector] = InjectorManager(config).init()

    @property
    def disabled(self):
        """
        If disabled, no tracers, filters, collectors will be initialized.
        """
        return self.config.disabled

    @property
    def backend_args(self):
        """
        Config for ``self._backend_imp``.
        """
        return self.config.backend_args

    def poll_all(self):
        """
        Poll all tracers. Depends on ``self.poll``.
        """
        return self._backend.map(self.poll, self.tracers)

    def poll(self, tracer: Tracer):
        """
        Poll a tracer. Should be implemented by subclass.
        """
        raise NotImplementedError

    def summary(self) -> dict:
        """
        Get a summary of all collectors.
        """
        return {
            self.__class__.__name__: {
                collector.__class__.__name__: collector.summary() for collector in self.collectors
            }
        }

    def start_polling(self):
        """
        Start polling. Poller will call ``self.poll_all`` periodically.
        """
        logger.info(f"Start polling {self.__class__.__name__}")
        self.poller.start(self.poll_all)

    def shutdown(self):
        """
        Shutdown the monitor.
        """
        self.poller.shutdown()
        self.poller.wait()
        self._backend.shutdown()
        for c in self.collectors:
            c.shutdown()
        for i in self.injectors:
            i.shutdown()

    def _inject_extra_info(self, data: namedtuple) -> namedtuple:
        patch_kwargs = {}
        for injector in self.injectors:
            patch_kwargs.update(injector.get_patch_kwargs(data, patch_kwargs))
        data = Injector.patch(data, patch_kwargs)
        return data

    @cache
    def _get_callback_fn(self, tracer) -> Callable[[namedtuple], None]:
        def _(data):
            try:
                data = self._inject_extra_info(data)

                for filter in self.filters:
                    data = filter(data)
                    if not data:
                        return
                for collector in self.collectors:
                    collector.emit(tracer, data)
            except Exception as e:
                logger.exception(e)

        return _

    def _set_callback(self, host, tracer):
        """
        Wrap tracer callback with filters and collectors.
        """
        tracer.set_callback(host, self._get_callback_fn(tracer))
