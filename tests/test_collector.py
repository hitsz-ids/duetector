from collections import namedtuple

import pytest

from duetector.collectors.db import DBCollector
from duetector.collectors.models import Tracking
from duetector.managers.collector import CollectorManager
from duetector.utils import get_boot_time_duration_ns

timestamp = 13205215231927
datetime = get_boot_time_duration_ns(timestamp)


@pytest.fixture
def config(full_config):
    yield CollectorManager(full_config).config._config_dict


@pytest.fixture
def dbcollector(config):
    yield DBCollector(config)


@pytest.fixture
def data_t():
    d = namedtuple("Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"])

    yield d(
        pid=9999,
        uid=9999,
        gid=9999,
        comm="dummy",
        fname="dummy.file",
        timestamp=timestamp,
        custom="dummy-xargs",
    )


def test_dbcollector(dbcollector: DBCollector, data_t):
    dbcollector.emit("dummy", data_t)
    dbcollector.shutdown()
    assert dbcollector.summary() == {
        "dummy": {
            "count": 1,
            "first at": datetime,
            "last": Tracking(
                tracer="dummy",
                pid=9999,
                uid=9999,
                gid=9999,
                comm="dummy",
                cwd=None,
                fname="dummy.file",
                dt=datetime,
                extended={"custom": "dummy-xargs"},
            ),
        }
    }


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
