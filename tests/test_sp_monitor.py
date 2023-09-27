import time
from copy import deepcopy
from pathlib import Path

import pytest

from duetector.monitors.subprocess_monitor import SubprocessMonitor
from duetector.tracers.base import SubprocessTracer

_HERE = Path(__file__).parent


class DummySpTracer(SubprocessTracer):
    default_config = {
        **SubprocessTracer.default_config,
    }

    comm = [(_HERE / "bin" / "dummy_process.py").as_posix()]


@pytest.fixture
def config(full_config):
    c = deepcopy(full_config)

    c.update(
        **{
            "monitor": {
                "subprocess": {
                    "auto_init": False,
                }
            },
        }
    )
    yield c


@pytest.fixture
def sp_monitor(config) -> SubprocessMonitor:
    sp_monitor = SubprocessMonitor(config)
    sp_monitor.tracers = [DummySpTracer()]
    sp_monitor.init()
    yield sp_monitor
    sp_monitor.shutdown()


def test_sp_monitor(sp_monitor: SubprocessMonitor):
    assert sp_monitor
    assert sp_monitor.tracers
    assert sp_monitor.filters
    assert sp_monitor.collectors
    assert sp_monitor.host
    assert not sp_monitor.auto_init
    assert sp_monitor.timeout
    popens = list(sp_monitor.host.tracers.values())
    time.sleep(2.5)
    sp_monitor.poll_all()
    time.sleep(0.5)
    sp_monitor.shutdown()
    for popen in popens:
        assert popen.poll() == 0

    # assert sp_monitor.summary()["SubprocessMonitor"]["DBCollector"]["dummysptracer"]["count"]


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
