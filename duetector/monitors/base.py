from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

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

    tracers: List[Tracer]
    """
    A list of tracers, should be initialized by ``TracerManager``
    """

    filters: List[Filter]
    """
    A list of filters, should be initialized by ``FilterManager``
    """
    collectors: List[Collector]
    """
    A list of collectors, should be initialized by ``CollectorManager``
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

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config)
        self._backend = self._backend_imp(**self.backend_args._config_dict)
        self.poller = Poller(self.config._config_dict)

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
        return [self._backend.submit(self.poll, tracer) for tracer in self.tracers]

    def poll(self, tracer: Tracer):
        """
        Poll a tracer. Should be implemented by subclass.
        """
        raise NotImplementedError

    def summary(self) -> Dict:
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
