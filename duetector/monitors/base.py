import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from duetector.collectors.base import Collector
from duetector.config import Configuable
from duetector.filters.base import Filter
from duetector.log import logger
from duetector.tracers.base import Tracer


class Poller(Configuable):
    config_scope = "poller"
    default_config = {
        "interval_ms": 500,
    }

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(config=config, *args, **kwargs)
        self._thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()

    @property
    def interval_ms(self):
        return self.config.interval_ms

    def start(self, func, *args, **kwargs):
        if self._thread:
            raise RuntimeError("Poller thread is already started, try shutdown and wait first.")

        def _poll():
            while not self.shutdown_event.is_set():
                func(*args, **kwargs)
                self.shutdown_event.wait(timeout=self.interval_ms / 1000)

        self._thread = threading.Thread(target=_poll)
        self.shutdown_event.clear()
        self._thread.start()

    def shutdown(self):
        self.shutdown_event.set()

    def wait(self, timeout_ms=None):
        timeout = (timeout_ms or self.interval_ms * 3) / 1000
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            # FIXME: should we raise an exception here?
            logger.warning("Poller thread is still alive after timeout")
            self.shutdown()
        else:
            self._thread = None
            self.shutdown_event.clear()


class Monitor(Configuable):
    """
    A base class for all monitors

    A monitor is a collection of tracers, filters and collectors,
    record host and tracer, provide a way to poll data
    """

    tracers: List[Tracer]
    filters: List[Filter]
    collectors: List[Collector]

    config_scope = "monitor"

    default_config = {
        "disabled": False,
        "backend_args": {
            "max_workers": 10,
        },
        "poller": {
            **Poller.default_config,
        },
    }

    _backend_imp = ThreadPoolExecutor

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config)
        self._backend = self._backend_imp(**self.backend_args.config_dict)
        self.poller = Poller(self.config.config_dict)

    @property
    def disabled(self):
        return self.config.disabled

    @property
    def backend_args(self):
        return self.config.backend_args

    def poll_all(self):
        return [self._backend.submit(self.poll, tracer) for tracer in self.tracers]

    def poll(self, tracer: Tracer):
        raise NotImplementedError

    def summary(self) -> Dict:
        return {collector.__class__.__name__: collector.summary() for collector in self.collectors}

    def start_polling(self):
        logger.info(f"Start polling {self.__class__.__name__}")
        self.poller.start(self.poll_all)

    def shutdown(self):
        self.poller.shutdown()
        self.poller.wait()
        self._backend.shutdown(cancel_futures=True)
        for c in self.collectors:
            c.shutdown()
