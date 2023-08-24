from collections import namedtuple

import pytest

from duetector.collectors.db import DBCollector
from duetector.collectors.models import Tracking
from duetector.managers import CollectorManager


@pytest.fixture
def config(full_config):
    yield CollectorManager(full_config).config.config_dict


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
        timestamp=13205215231927,
        custom="dummy-xargs",
    )


def test_dbcollector(dbcollector: DBCollector, data_t):
    dbcollector.emit("dummy", data_t)
    assert dbcollector.summary() == {
        "dummy": {
            "count": 1,
            "first at": 13205215231927,
            "last": Tracking(
                tracer="dummy",
                pid=9999,
                uid=9999,
                gid=9999,
                comm="dummy",
                cwd=None,
                fname="dummy.file",
                timestamp=13205215231927,
                extended={"custom": "dummy-xargs"},
            ),
        }
    }


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
