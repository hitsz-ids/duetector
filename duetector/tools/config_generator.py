import copy
from pathlib import Path
from typing import Dict

import tomli_w

from duetector.analyzer.db import DBAnalyzer
from duetector.config import ConfigLoader
from duetector.log import logger
from duetector.managers.analyzer import AnalyzerManager
from duetector.managers.collector import CollectorManager
from duetector.managers.filter import FilterManager
from duetector.managers.tracer import TracerManager
from duetector.monitors import BccMonitor, ShMonitor
from duetector.service.config import ServerConfig


def _recursive_load(config_scope: str, config_dict: dict, default_config: dict):
    """
    Support .(dot) separated config_scope

    Example:
        >>> _recursive_load("monitor.bcc", {}, {"auto_init": True})
        {'monitor': {'bcc': {'auto_init': True}}}

    """
    *prefix, config_scope = config_scope.lower().split(".")
    last = config_dict
    for p in prefix:
        last = last.setdefault(p, {})
    last[config_scope] = copy.deepcopy(default_config)


class ConfigGenerator:
    """
    Tools for generate config file by inspecting all modules.

    Args:
        load (bool): Load config file or not.
        path (str): Path to config file.
        load_env (bool): Load environment variables or not.
        include_extension (bool): Include extensions or not.
    """

    HEADLINES = """# This is a auto generated config file for duetector🔍
# You can modify this file to change duetector's behavior
# For more information, please visit https://github.com/hitsz-ids/duetector

# All config keys will be converted to lower case.
# It's ok to use upper case or camel case for readability.

"""

    managers = [FilterManager, TracerManager, CollectorManager, AnalyzerManager]
    """
    All managers to inspect.
    """

    monitors = [BccMonitor, ShMonitor]
    """
    All monitors to inspect.
    """

    others = [ServerConfig]

    def __init__(
        self,
        load: bool = True,
        path: bool = None,
        load_env: bool = True,
        include_extension: bool = True,
    ):
        # dynamic_config containers all default config for all modules, including extensions
        self.dynamic_config = {}

        for manager in self.managers:
            m = manager(include_extension=include_extension)
            _recursive_load(m.config_scope, self.dynamic_config, m.default_config)
            for c in m.init(ignore_disabled=False):
                _recursive_load(
                    c.config_scope,
                    self.dynamic_config[m.config_scope],
                    c.default_config,
                )

        for m in self.monitors:
            _recursive_load(m.config_scope, self.dynamic_config, m.default_config)

        for o in self.others:
            _recursive_load(o.config_scope, self.dynamic_config, o.default_config)
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
        """
        Generate config file to dump_path.
        """
        dump_path = Path(dump_path).expanduser().absolute()
        logger.info(f"Dumping dynamic config to {dump_path}")

        with dump_path.open("w") as f:
            f.write(self.HEADLINES)

        with dump_path.open("ab") as f:
            tomli_w.dump(self.dynamic_config, f)


if __name__ == "__main__":
    _HERE = Path(__file__).parent
    c = ConfigGenerator(load=False, load_env=False, include_extension=False)
    config_path = _HERE / ".." / "static/config.toml"
    c.generate(config_path)
