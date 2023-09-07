import threading
from typing import Any, Dict, Optional

from duetector.config import Configuable
from duetector.log import logger


class Poller(Configuable):
    """
    A wrapper for ``threading.Thread``

    Special config:
        - interval_ms: Polling interval in milliseconds
    """

    config_scope = "poller"
    """
    Config scope for this poller.
    """

    default_config = {
        "interval_ms": 500,
    }
    """
    Default config for this poller.
    """

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
        """
        Polling interval in milliseconds
        """
        return self.config.interval_ms

    def start(self, func, *args, **kwargs):
        """
        Start a poller thread, until ``shutdown`` is called.

        Exceptions:
            - RuntimeError: If poller thread is already started.
        """
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
        """
        Shutdown poller thread. It's safe to call this method multiple times.

        After shutdown, ``wait`` should be called to wait for the thread to exit.
        """
        self.shutdown_event.set()

    def wait(self, timeout_ms=None):
        """
        Wait for poller thread to exit.

        Call this method after ``shutdown``.
        """
        if not self._thread:
            return

        timeout = (timeout_ms or self.interval_ms * 3) / 1000
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            # FIXME: should we raise an exception here?
            logger.warning("Poller thread is still alive after timeout")
            self.shutdown()
        else:
            self._thread = None
            self.shutdown_event.clear()
