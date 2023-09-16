from collections import namedtuple
from typing import Any, Callable, Dict, NamedTuple, Optional, Type

import pytest

from duetector.collectors.models import Tracking
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors.bcc_monitor import BccMonitor, Monitor
from duetector.tracers.base import BccTracer, Tracer
from duetector.utils import get_boot_time_duration_ns

timestamp = 13205215231927
datetime = get_boot_time_duration_ns(timestamp)


class MockTracer(Tracer):
    data_t = namedtuple(
        "DummyTracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"]
    )

    @classmethod
    def get_dummy_data(cls):
        return cls.data_t(
            pid=9999,
            uid=9999,
            gid=9999,
            comm="dummy",
            fname="dummy.file",
            timestamp=timestamp,
            custom="dummy-xargs",
        )

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled

    def attach(self, host):
        host["tracer"] = self

    def detach(self, host):
        del host["tracer"]

    def get_poller(self, host) -> Callable:
        def _():
            data = self.get_dummy_data()
            for callback in host["callback"]:
                callback(data)

        return _

    def set_callback(self, host, callback: Callable[[NamedTuple], None]):
        def _(data):
            return callback(data)

        host["callback"].append(_)


class MockMonitor(Monitor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]],
        mock_cls: Type[Monitor],
        mock_tracer: Type[Tracer],
    ):
        self.default_config = mock_cls.default_config
        self.config_scope = mock_cls.config_scope
        self.mock_cls = mock_cls
        super().__init__(config=config)

        tracer_config = TracerManager(config).config._config_dict

        self.tracers = [mock_tracer(tracer_config)]
        self.filters = FilterManager(config).init()
        self.collectors = CollectorManager(config).init()

        self.bpf_tracers = {}
        self.init()

    def init(self):
        for tracer in self.tracers:
            host = {
                "callback": [],
                "tracer": None,
            }
            tracer.attach(host)
            self.mock_cls._set_callback(self, host, tracer)
            self.bpf_tracers[tracer] = host

    def poll_all(self):
        self.mock_cls.poll_all(self)

    def poll(self, tracer: Tracer):
        self.mock_cls.poll(self, tracer)

    def summary(self) -> Dict:
        return self.mock_cls.summary(self)


@pytest.fixture
def bcc_monitor(full_config):
    class BccMockTracer(MockTracer, BccTracer):
        pass

    yield MockMonitor(full_config, BccMonitor, BccMockTracer)


def test_bcc_monitor(bcc_monitor: MockMonitor):
    bcc_monitor.poll_all()
    bcc_monitor.shutdown()
    assert bcc_monitor.summary()
    bcc_monitor.summary()["MockMonitor"]["DBCollector"]["BccMockTracer"]["last"] == Tracking(
        tracer="BccMockTracer",
        pid=9999,
        uid=9999,
        gid=9999,
        comm="dummy",
        cwd=None,
        fname="dummy.file",
        dt=datetime,
        extended={"custom": "dummy-xargs"},
    )


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
