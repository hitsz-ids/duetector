from pathlib import Path

import tomli_w

from duetector.config import ConfigLoader
from duetector.log import logger


class ConfigGenerator:
    managers = []
    monitors = []

    def __init__(self, load=True, path=None, load_env=True):
        # dynamic_config containers all default config for all modules, including extensions
        self.dynamic_config = {}

        # This will generate default config file if not exists
        if load:
            self.loaded_config = ConfigLoader(path, load_env, dump_when_load=False).load_config()

            # Now we merge loaded config into dynamic_config
            def _recursive_update(c, config):
                for k, v in config.items():
                    if not isinstance(v, dict):
                        c[k] = v
                    else:
                        c.setdefault(k, {})
                        _recursive_update(c[k], v)

            _recursive_update(self.dynamic_config, self.loaded_config)

    def generate(self, dump_path):
        dump_path = Path(dump_path).expanduser().absolute()
        logger.info(f"Dumping dynamic config to {dump_path}")

        with dump_path.open("wb") as f:
            tomli_w.dump(self.dynamic_config, f)


if __name__ == "__main__":
    _HERE = Path(__file__).parent
    c = ConfigGenerator(load=False)
    c.generate(_HERE / ".." / "static/config.dynamic.toml")
