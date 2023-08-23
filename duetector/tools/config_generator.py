from pathlib import Path
from typing import Dict

import tomli_w

from duetector.config import ConfigLoader
from duetector.log import logger
from duetector.managers import CollectorManager, FilterManager, TracerManager
from duetector.monitors import BccMonitor


def _recursive_load(config_scope: str, config_dict: dict, default_config: dict):
    *prefix, config_scope = config_scope.lower().split(".")
    last = config_dict
    for p in prefix:
        last = last.setdefault(p, {})
    last[config_scope] = default_config.copy()


class ConfigGenerator:
    """
    Tools for generate config file by inspecting all modules
    """

    HEADLINES = """# This is a auto generated config file for duetector🔍
# You can modify this file to change duetector's behavior
# For more information, please visit https://github.com/hitsz-ids/duetector

# All config keys will be converted to lower case.
# It's ok to use upper case or camel case for readability.

"""

    managers = [FilterManager, TracerManager, CollectorManager]
    monitors = [BccMonitor]

    def __init__(self, load=True, path=None, load_env=True):
        # dynamic_config containers all default config for all modules, including extensions
        self.dynamic_config = {}

        for manager in self.managers:
            m = manager()
            _recursive_load(m.config_scope, self.dynamic_config, m.default_config)
            for c in m.init(ignore_disabled=False):
                _recursive_load(
                    c.config_scope,
                    self.dynamic_config[m.config_scope],
                    c.default_config,
                )

        # Support .(dot) separated config_scope
        for m in self.monitors:
            _recursive_load(m.config_scope, self.dynamic_config, m.default_config)

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

        with dump_path.open("w") as f:
            f.write(self.HEADLINES)

        with dump_path.open("ab") as f:
            tomli_w.dump(self.dynamic_config, f)


if __name__ == "__main__":
    _HERE = Path(__file__).parent
    c = ConfigGenerator(load=False)
    config_path = _HERE / ".." / "static/config.toml"
    c.generate(config_path)
