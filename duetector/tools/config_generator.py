from pathlib import Path
from typing import Dict

import tomli_w

from duetector.config import ConfigLoader
from duetector.log import logger
from duetector.managers import CollectorManager, FilterManager, TracerManager
from duetector.monitors import BccMonitor


class ConfigGenerator:
    managers = [FilterManager, TracerManager, CollectorManager]
    monitors = [BccMonitor]

    def __init__(self, load=True, path=None, load_env=True):
        # dynamic_config containers all default config for all modules, including extensions
        self.dynamic_config = {}

        for manager in self.managers:
            m = manager()
            manager_scope: Dict = self.dynamic_config.setdefault(m.config_scope.lower(), {})
            manager_scope.update(m.default_config)

            for c in m.init(ignore_disabled=False):
                config_scpre: Dict = manager_scope.setdefault(c.config_scope.lower(), {})
                config_scpre.update(c.default_config)

        # Support .(dot) separated config_scope
        for m in self.monitors:
            *prefix, config_scope = m.config_scope.split(".")
            last = self.dynamic_config
            for p in prefix:
                last = last.setdefault(p, {})
            last[config_scope] = m.default_config

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
