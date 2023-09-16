import os

os.environ["DUETECTOR_LOG_LEVEL"] = "DEBUG"


from pathlib import Path

import pytest

from duetector.config import ConfigLoader

_HERE = Path(__file__).parent

CONFIG = (_HERE / "config.toml").read_text()


@pytest.fixture
def full_config_file(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(CONFIG)
    yield config_file


@pytest.fixture
def full_config(full_config_file):
    yield ConfigLoader(full_config_file, load_env=False, dump_when_load=False).load_config()
