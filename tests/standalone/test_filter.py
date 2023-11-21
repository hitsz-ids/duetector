from collections import namedtuple

import pytest

from duetector.config import ConfigLoader
from duetector.filters.pattern import PatternFilter
from duetector.managers.filter import FilterManager

data_t = namedtuple(
    "Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom", "gcustom"]
)


@pytest.fixture
def config(full_config):
    yield FilterManager(full_config).config._config_dict


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


@pytest.fixture
def config_loader(full_config_file):
    yield ConfigLoader(full_config_file, load_env=True)


@pytest.fixture
def env_config(config_loader: ConfigLoader, monkeypatch):
    prefix = config_loader.ENV_PREFIX
    sep = config_loader.ENV_SEP
    monkeypatch.setenv(f"{prefix}filter{sep}patternfilter{sep}exclude_ecustom", "ignore_ecustom")
    monkeypatch.setenv(
        f"{prefix}filter{sep}patternfilter{sep}re_exclude_egcustom",
        '["ignore_ecustom*"]',
    )
    yield FilterManager(config_loader.load_config()).config._config_dict


@pytest.fixture
def env_pattern_filter(env_config):
    yield PatternFilter(env_config)


env_passed = {
    **passed,
    "ecustom": "passed",
    "egcustom": "passed",
}
env_params = [
    (
        env_passed,
        True,
    ),
    (
        {
            **env_passed,
            "ecustom": "ignore_ecustom",  # Filtered
        },
        False,
    ),
    (
        {
            **env_passed,
            "egcustom": "ignore_ecustom123",  # Filtered
        },
        False,
    ),
]

e_data_t = namedtuple(
    "Tracking",
    [
        "pid",
        "uid",
        "gid",
        "comm",
        "fname",
        "timestamp",
        "custom",
        "gcustom",
        "ecustom",
        "egcustom",
    ],
)


@pytest.mark.parametrize("data_args, passed", env_params)
def test_filter_envs(env_pattern_filter, data_args, passed):
    data = e_data_t(**data_args)
    if passed:
        assert env_pattern_filter(data) == data
    else:
        assert env_pattern_filter(data) == None


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
