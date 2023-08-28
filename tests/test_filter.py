from collections import namedtuple

import pytest

from duetector.filters.pattern import PatternFilter
from duetector.managers import FilterManager

data_t = namedtuple(
    "Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom", "gcustom"]
)


@pytest.fixture
def config(full_config):
    yield FilterManager(full_config).config.config_dict


@pytest.fixture
def pattern_filter(config):
    yield PatternFilter(config)


passed = dict(
    pid=9999,
    uid=9999,
    gid=9999,
    comm="dummy",
    fname="dummy.file",
    timestamp=13205215231927,
    custom="passed",
    gcustom="passed",
)


params = [
    (passed, True),
    (
        {
            **passed,
            "uid": 0,  # Filtered
        },
        False,
    ),
    (
        {
            **passed,
            "fname": "/etc/ld.so.cache",  # Filtered
        },
        False,
    ),
    (
        {
            **passed,
            "fname": "/re/Filtered",  # Filtered
        },
        False,
    ),
    (
        {
            **passed,
            "custom": "ignore_custom",  # Filtered
        },
        False,
    ),
    (
        {
            **passed,
            "gcustom": "ignore_custom123",  # Filtered
        },
        False,
    ),
]


@pytest.mark.parametrize("data_args, passed", params)
def test_filter(pattern_filter, data_args, passed):
    data = data_t(**data_args)
    if passed:
        assert pattern_filter(data) == data
    else:
        assert pattern_filter(data) == None


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
