import subprocess
import threading
from collections import Counter
from io import DEFAULT_BUFFER_SIZE
from select import select
from typing import IO, Any, Callable, Dict, List, NamedTuple, Optional

import psutil

from duetector.collectors.base import Collector
from duetector.log import logger
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors.base import Monitor
from duetector.proto.subprocess import (
    EventMessage,
    InitMessage,
    StopMessage,
    StoppedMessage,
    dispatch_message,
)
from duetector.tracers.base import SubprocessTracer


class SubprocessHost:
    def __init__(
        self,
        timeout,
        backend,
        poll_szie=1024,
        bufsize=DEFAULT_BUFFER_SIZE * 4,
        kill_timeout=5,
        restart_times=0,
    ) -> None:
        self.tracers: Dict[SubprocessTracer, subprocess.Popen] = {}
        self.callbacks: Dict[SubprocessTracer, Callable[[NamedTuple], None]] = {}
        self.timeout = timeout
        self.backend = backend
        self.bufsize = bufsize
        self.poll_szie = poll_szie
        self.kill_timeout = kill_timeout

        self.restart_times = restart_times
        self.restart_counter: Counter = Counter()
        self.shutdown_event = threading.Event()
        self.shutdown_event.clear()

    def notify_init(self, tracer: SubprocessTracer):
        logger.debug(f"Notify init for tracer {tracer.__class__.__name__}")
        self._writeline(
            InitMessage.from_host(self, tracer).model_dump_json(),
            self.tracers[tracer].stdin,
        )

        self._poll(tracer, self.tracers[tracer].stdout.readline())

    def notify_stop(self, tracer: SubprocessTracer):
        logger.debug(f"Notify stop for tracer {tracer.__class__.__name__}")
        self._writeline(StopMessage.from_host(self).model_dump_json(), self.tracers[tracer].stdin)

    def notify_poll(self, tracer: SubprocessTracer):
        logger.debug(f"Notify poll for tracer {tracer.__class__.__name__}")
        self._writeline(EventMessage.from_host(self).model_dump_json(), self.tracers[tracer].stdin)

    def _writeline(self, json_str: str, io: IO):
        if not json_str.endswith("\n"):
            json_str += "\n"
        io.write(json_str)
        io.flush()

    def attach(self, tracer: SubprocessTracer):
        if self.shutdown_event.is_set():
            raise RuntimeError("Host already shutdown")

        p = subprocess.Popen(
            tracer.comm,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,  # FIXME: We currently using a text proto, may change to binary proto in the future
            bufsize=self.bufsize,
        )
        self.tracers[tracer] = p
        self.notify_init(tracer)

    def detach(self, tracer: SubprocessTracer):
        if tracer in self.tracers:
            p = self.tracers.get(tracer)
            try:
                p = psutil.Process(p.pid)
            except psutil.NoSuchProcess:
                # Already stopped
                logger.warning("Detaching a stopped tracer")
                self.poll(tracer)
                self.tracers.pop(tracer)
                return

            try:
                self.notify_stop(tracer)
                logger.info(f"Detaching {tracer}")
                p.terminate()
                logger.info("Wating for subprocess to stop")
                p.wait(self.kill_timeout)
            except psutil.TimeoutExpired:
                logger.warning("Timeout for terminate subprocess, kill it.")
                p.kill()
            self.poll(tracer)
            self.tracers.pop(tracer)
        else:
            logger.warning("Tracer not attached, ignore")

    def shutdown(self):
        logger.info("Shutting down host")
        self.shutdown_event.set()
        for tracer in list(self.tracers):
            self.detach(tracer)

    def is_alive(self, tracer: SubprocessTracer):
        p = self.tracers[tracer]
        try:
            psutil_p = psutil.Process(p.pid)
        except psutil.NoSuchProcess:
            return False
        return psutil_p.is_running()

    def poll(self, tracer: SubprocessTracer):
        """
        Poll a tracer.
        """
        p = self.tracers[tracer]
        if not self.is_alive(tracer):
            if self.restart_times == 0:
                return
            if (
                self.restart_counter[tracer] >= self.restart_times
                and not self.shutdown_event.is_set()
            ):
                logger.warning(
                    f"Tracer {tracer.__class__.__name__} restart times exceed limit, stop it."
                )
                self.detach(tracer)
                return
            logger.warning(f"Tracer {tracer.__class__.__name__} stopped, restart it.")
            self.restart_counter[tracer] += 1
            self.attach(tracer)
            p = self.tracers[tracer]
            # Poll next time

        else:
            logger.debug(f"Polling tracer {tracer.__class__.__name__}")
            self.notify_poll(tracer)
            ready = select([p.stdout.fileno()], [], [], self.timeout)[0]
            poll_count = 0
            while ready and poll_count < self.poll_szie and not self.shutdown_event.is_set():
                poll_count += 1
                output = p.stdout.readline()
                if not output:
                    break
                self._poll(tracer, output)
                ready = select([p.stdout.fileno()], [], [], self.timeout)[0]
            logger.debug(f"Total poll count: {poll_count}")

    def _poll(self, tracer: SubprocessTracer, output):
        if not output:
            # Empty output
            return
        msg = dispatch_message(output)
        if not msg:
            return
        if isinstance(msg, EventMessage):
            self.callbacks[tracer](msg.serialize_namedtuple())
        if isinstance(msg, StoppedMessage):
            self.detach(tracer)
        if isinstance(msg, InitMessage):
            logger.info(f"Tracer {tracer.__class__.__name__} initialized")

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


class SubprocessMonitor(Monitor):
    config_scope = "monitor.subprocess"

    default_config = {
        **Monitor.default_config,
        "auto_init": True,
        "timeout": 0.01,
        "kill_timeout": 5,
        "pool_size": 1024,
        "bufsize": DEFAULT_BUFFER_SIZE * 4,
        "restart_times": 0,
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
        Timeout for poll.
        """
        return float(self.config.timeout)

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

    @property
    def poll_szie(self):
        """
        Poll size for subprocess.
        """
        return float(self.config.pool_size)

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
            backend=self._backend,
            bufsize=self.bufsize,
            poll_szie=self.poll_szie,
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

    def poll_all(self):
        return self.host.poll_all()

    def poll(self, tracer: SubprocessTracer):  # type: ignore
        return self.host.poll(tracer)
