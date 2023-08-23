from collections import namedtuple

import pytest

from duetector.filters.base import DefaultFilter
from duetector.managers import FilterManager


@pytest.fixture
def config(full_config):
    yield FilterManager(full_config).config.config_dict


@pytest.fixture
def default_filter(config):
    yield DefaultFilter(config)


def test_default_filter(default_filter):
    data_t = namedtuple("Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"])
    data = data_t(
        pid=9999,
        uid=9999,
        gid=9999,
        comm="dummy",
        fname="dummy.file",
        timestamp=13205215231927,
        custom="dummy-xargs",
    )
    assert default_filter(data) == data

    data = data_t(
        pid=9999,
        uid=9999,
        gid=9999,
        comm="dummy",
        fname="/etc/ld.so.cache",
        timestamp=13205215231927,
        custom="dummy-xargs",
    )
    assert default_filter(data) == None


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
