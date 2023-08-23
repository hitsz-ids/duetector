import pytest

from duetector.config import ConfigLoader, Configuable

CONFIG_CONTENT = """

outofscope = "outofscope"

[scope]
default_a = "b"

[scope.subScope]
default_b = "c"

"""


@pytest.fixture
def config_file(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(CONFIG_CONTENT)
    yield config_file


@pytest.fixture
def config_loader(config_file):
    yield ConfigLoader(config_file)


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


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
