from pathlib import Path
from typing import Any, Dict, Optional

import tomli

from duetector.exceptions import ConfigFileNotFoundError
from duetector.log import logger


class Config:
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        if not config_dict:
            config_dict = {}
        self.config_dict: Dict[str, Any] = config_dict

    def __repr__(self) -> str:
        return str(self.config_dict)

    def __getattr__(self, name):
        if isinstance(self.config_dict.get(name), dict):
            return Config(self.config_dict[name])

        return self.config_dict.get(name, None)

    def __bool__(self):
        return bool(self.config_dict)


class ConfigLoader:
    def __init__(self, path):
        self.config_path: Path = Path(path).absolute()

    def __repr__(self) -> str:
        return f"ConfigLoader({self.config_path})"

    def _init_default_modules(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        config_dict.setdefault("tracer", {})
        config_dict.setdefault("collector", {})
        config_dict.setdefault("filter", {})
        config_dict.setdefault("monitor", {})
        return config_dict

    def load_config(self) -> Config:
        logger.info(f"Loading config from {self.config_path}")
        if not self.config_path.exists():
            raise ConfigFileNotFoundError(f"Config file:{self.config_path} not found.")

        try:
            with self.config_path.open("rb") as f:
                config = tomli.load(f)
                config = self._init_default_modules(config)
                return Config(config)
        except tomli.TOMLDecodeError as e:
            logger.error(f"Error loading config: {e}")
            raise e


class Configuable:
    default_config = {}
    config_spec = None

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        if not config:
            config = {}
        if self.config_spec:
            config = config.get(self.config_spec, {})
        c = self.default_config.copy()
        c.update(config)
        self.config = Config(c)
        logger.debug(f"{self} initializing...")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.config})"
