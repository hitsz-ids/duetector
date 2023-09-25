import subprocess
from io import DEFAULT_BUFFER_SIZE, StringIO
from typing import Any, Callable, Dict, List, NamedTuple, Optional

import psutil

from duetector.collectors.base import Collector
from duetector.log import logger
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors.base import Monitor
from duetector.tracers.base import SubprocessTracer


class SubprocessHost:
    def __init__(self, timeout, backend, bufsize=DEFAULT_BUFFER_SIZE * 4, kill_timeout=5) -> None:
        self.tracers: Dict[SubprocessTracer, subprocess.Popen] = {}
        self.callbacks: Dict[SubprocessTracer, Callable[[NamedTuple], None]] = {}
        self.timeout = timeout
        self.backend = backend
        self.bufsize = bufsize
        self.kill_timeout = kill_timeout

    def attach(self, tracer: SubprocessTracer):
        p = subprocess.Popen(
            tracer.comm,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,  # FIXME: We currently using a text proto, may change to binary proto in the future
            bufsize=self.bufsize,
        )
        self.tracers[tracer] = p

    def detach(self, tracer):
        if tracer in self.tracers:
            p = self.tracers.pop(tracer)
            try:
                # TODO: Write stop message for notify subprocess to stop
                # tracer.notify_stop(p.stdin)
                p.terminate()
                logger.info("Wating for subprocess to stop")
                p.wait(self.kill_timeout)
            except psutil.TimeoutExpired:
                logger.warning("Timeout for terminate subprocess, kill it.")
                p.kill()
            self.poll(tracer)

    def shutdown(self):
        for tracer in self.tracers:
            self.detach(tracer)

    def poll(self, tracer):
        """
        Poll a tracer.
        """
        p = self.tracers[tracer]
        # TODO: Write poll message for keepalive
        tracer.notify_poll(p.stdin)
        outputs = p.stdout.readlines()
        callback = self.callbacks[tracer]
        for output in outputs:
            callback(tracer.deserialize(output))

    def poll_all(self):
        """
        Poll all tracers.
        """
        return [self.backend.submit(self.poll, tracer) for tracer in self.tracers]

    def set_callback(self, tracer, callback):
        """
        Set callback for tracer.
        """
        self.callbacks[tracer] = callback


class SubprocessMonitor(Monitor):
    default_config = {
        **Monitor.default_config,
        "auto_init": True,
        "timeout": 5,
        "kill_timeout": 5,
        "bufsize": DEFAULT_BUFFER_SIZE * 4,
    }

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

    @property
    def kill_timeout(self):
        """
        Timeout for kill subprocess.
        """
        return int(self.config.kill_timeout)

    @property
    def bufsize(self):
        """
        Buffer size for subprocess.
        """
        return int(self.config.bufsize)

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config=config, *args, **kwargs)
        if self.disabled:
            logger.info("SubprocessMonitor disabled")
            self.tracers = []
            self.filters = []
            self.collectors = []
            return

        self.tracers: List[SubprocessTracer] = TracerManager(config).init(tracer_type=SubprocessTracer)  # type: ignore
        self.filters: List[Callable] = FilterManager(config).init()
        self.collectors: List[Collector] = CollectorManager(config).init()

        self.host = SubprocessHost(
            timeout=self.timeout,
            backend=self.backend,
            bufsize=self.bufsize,
            kill_timeout=self.kill_timeout,
        )
        if self.auto_init:
            self.init()

    def init(self):
        for tracer in self.tracers:
            tracer.attach(self.host)
            self._set_callback(self.host, tracer)
            logger.info(f"Tracer {tracer.__class__.__name__} attached")

    def _set_callback(self, host, tracer):
        def _(data):
            for filter in self.filters:
                data = filter(data)
                if not data:
                    return

            for collector in self.collectors:
                collector.emit(tracer, data)

        tracer.set_callback(host, _)

    def shutdown(self):
        self.host.shutdown()
        super().shutdown()
