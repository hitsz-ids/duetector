import pytest

from duetector.config import ConfigLoader, Configuable
from duetector.tools.config_generator import ConfigGenerator

CONFIG_CONTENT = """

outofscope = "outofscope"

[scope]
default_a = "b"

[scope.subscope]
default_b = "c"

"""


@pytest.fixture
def config_file(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(CONFIG_CONTENT)
    yield config_file


@pytest.fixture
def config_loader(config_file):
    yield ConfigLoader(config_file, load_env=True)


@pytest.fixture
def config_generator(config_file):
    yield ConfigGenerator(load=True, path=config_file, load_env=True)


class ConfiguableTesting(Configuable):
    default_config = {"default_a": "a", "default_b": "b"}
    config_scope = "scope"


class ConfiguableSubscopeTesting(Configuable):
    default_config = {"default_a": "a", "default_b": "b"}
    config_scope = "scope.subscope"


def test_config(config_loader: ConfigLoader):
    config = config_loader.load_config()

    config_in_obj = ConfiguableTesting(config).config
    assert config_in_obj.outofscope == None
    assert config_in_obj.default_a == "b"
    assert config_in_obj.default_b == "b"

    config_subscope_in_obj = ConfiguableSubscopeTesting(config).config
    assert config_subscope_in_obj.outofscope == None
    assert config_subscope_in_obj.default_a == "a"
    assert config_subscope_in_obj.default_b == "c"


def test_load_env(config_loader: ConfigLoader, monkeypatch):
    prefix = config_loader.ENV_PREFIX
    sep = config_loader.ENV_SEP
    monkeypatch.setenv(f"{prefix}ENVSCOPE{sep}DEFAULT_A", "env_a")
    monkeypatch.setenv(f"{prefix}ENVSCOPE{sep}ENVSUBSCOPE{sep}DEFAULT_B", "env_b")
    config = config_loader.load_config()

    assert config["ENVSCOPE".lower()]["DEFAULT_A".lower()] == "env_a"
    assert config["ENVSCOPE".lower()]["ENVSUBSCOPE".lower()]["DEFAULT_B".lower()] == "env_b"


def test_generate(config_generator: ConfigGenerator, tmpdir):
    generated_file = tmpdir.join("config-generated.toml")
    config_generator.generate(generated_file)
    assert generated_file.exists()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
