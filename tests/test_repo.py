from pathlib import Path

import pytest
import tomli

from duetector.config import ConfigLoader
from duetector.tools.config_generator import ConfigGenerator

_HERE = Path(__file__).parent.absolute()


def test_repo_config_uptodate(tmpdir):
    # Check default config in repo is up to date
    CONFIG_IN_REPO = _HERE / ".." / "duetector/static/config.toml"
    GENERATED_CONFIG = tmpdir.join("g-default-config.toml")
    config_generator = ConfigGenerator(load=False, load_env=False)
    config_generator.generate(GENERATED_CONFIG)
    assert GENERATED_CONFIG.exists()

    generated_config = tomli.loads(GENERATED_CONFIG.read_text(encoding="utf-8"))
    repo_config = ConfigLoader(
        path=CONFIG_IN_REPO,
        load_env=False,
        dump_when_load=False,
        config_dump_dir=None,
        generate_config=False,
    ).load_config()
    assert generated_config == repo_config


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
