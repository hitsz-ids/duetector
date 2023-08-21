import pytest

from duetector.config import ConfigLoader

CONFIG = """
[tracer]


[filter]

[collector]


[monitor.bcc]

[collector.SQLiteCollector.db]
debug=true

"""


@pytest.fixture
def full_config_file(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(CONFIG)
    yield config_file


@pytest.fixture
def full_config(full_config_file):
    yield ConfigLoader(full_config_file).load_config()
