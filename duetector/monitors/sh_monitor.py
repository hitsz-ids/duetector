from __future__ import annotations

import subprocess
from collections import namedtuple
from datetime import datetime
from typing import Any, Callable

from duetector.filters.base import Filter
from duetector.injectors.base import Injector
from duetector.managers.injector import InjectorManager

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.collectors.base import Collector
from duetector.log import logger
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors.base import Monitor
from duetector.tracers.base import ShellTracer


class ShTracerHost:
    """
    Host for Shell, provide a way to poll shell command.

    Use ``subprocess.Popen`` to run shell command.
    """

    def __init__(self, backend, timeout=5):
        self.tracers: dict[ShellTracer, list[str]] = {}
        self.callbacks: dict[ShellTracer, Callable[[namedtuple], None]] = {}
        self.timeout = timeout
        self.backend = backend

    def attach(self, tracer):
        self.tracers[tracer] = tracer.comm

    def detach(self, tracer):
        if tracer in self.tracers:
            self.tracers.pop(tracer)

    @cache
    def get_poller(self, tracer) -> Callable[[None], None]:
        """
        Provide a callback function for ``Poller``.

        Use ``subprocess.Popen`` to run shell command, pipe stdout to callback.
        """
        comm = self.tracers[tracer]
        enable_cache = tracer.enable_cache

        def _():
            p = subprocess.Popen(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait(self.timeout)
            output = p.stdout.read().decode("utf-8")
            if enable_cache:
                if output == tracer.get_cache():
                    # No change, no need to call callback
                    return
                tracer.set_cache(output)

            callback = self.callbacks[tracer]
            callback(tracer.data_t(output=output, dt=datetime.now()))

        return _

    def poll(self, tracer):
        """
        Poll a tracer.
        """
        self.get_poller(tracer)()

    def poll_all(self):
        """
        Poll all tracers.
        """
        return self.backend.map(self.poll, self.tracers)

    def set_callback(self, tracer, callback):
        """
        Set callback for tracer.
        """
        self.callbacks[tracer] = callback


class ShMonitor(Monitor):
    """
    A monitor for shell command.
    """

    config_scope = "monitor.sh"
    """
    Config scope for this monitor.
    """

    default_config = {
        **Monitor.default_config,
        "auto_init": True,
        "timeout": 5,
    }
    """
    Default config for this monitor.

    Two sub-configs are available:
        - auto_init: Auto init tracers when init monitor.
        - timeout: Timeout for shell command.
    """

    @property
    def auto_init(self):
        """
        Auto init tracers when init monitor.
        """
        return self.config.auto_init

    @property
    def timeout(self):
        """
        Timeout for shell command.
        """
        return int(self.config.timeout)

    def __init__(self, config: dict[str, Any] | None = None, *args, **kwargs):
        super().__init__(config=config, *args, **kwargs)
        if self.disabled:
            logger.info("ShMonitor disabled")
            return

        self.tracers: list[ShellTracer] = TracerManager(config).init(tracer_type=ShellTracer)  # type: ignore

        self.host = ShTracerHost(self._backend, self.timeout)
        if self.auto_init:
            self.init()

    def init(self):
        for tracer in self.tracers:
            tracer.attach(self.host)
            self._set_callback(self.host, tracer)
            logger.info(f"Tracer {tracer.__class__.__name__} attached")

    def poll_all(self):
        return self.host.poll_all()

    def poll(self, tracer: ShellTracer):  # type: ignore
        return self.host.poll(tracer)


if __name__ == "__main__":
    m = ShMonitor()
    print(m)
    while True:
        try:
            m.poll_all()
        except KeyboardInterrupt:
            print(m.summary())
            exit()
