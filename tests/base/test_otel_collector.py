import json
import os
from collections import namedtuple
from copy import deepcopy

import pytest

from duetector.collectors.otel import OTelCollector
from duetector.utils import get_boot_time_duration_ns

timestamp = 13205215231927
datetime = get_boot_time_duration_ns(timestamp)


@pytest.fixture
def data_t():
    d = namedtuple("Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"])

    yield d(
        pid=os.getpid(),
        uid=9999,
        gid=9999,
        comm="dummy",
        fname="dummy.file",
        timestamp=timestamp,
        custom="dummy-xargs",
    )


@pytest.fixture
def config(full_config):
    c = deepcopy(full_config)
    yield c["collector"]


@pytest.fixture
def collector(config):
    return OTelCollector(config)


def test_dbcollector(collector: OTelCollector, data_t, capsys):
    collector.emit("dummy", data_t)
    collector.shutdown()
    # FIXME: how to test this? Code below doesn't work, cannot capture stdout
    # captured = capsys.readouterr()
    # tracking = json.loads(captured.out)
    # assert tracking["attributes"]
    # for k in ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"]:
    #     assert k in tracking["attributes"]


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
