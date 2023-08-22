import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union

import tomli

from duetector.exceptions import ConfigFileNotFoundError
from duetector.log import logger

_HERE = Path(__file__).parent
DEFAULT_CONFIG = _HERE / "static" / "config.toml"
CONFIG_PATH = Path("~/.config/duetector/config.toml").expanduser()


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
    def __init__(self, path: Union[str, Path] = CONFIG_PATH):
        self.config_path: Path = Path(path).absolute()

        if not self.config_path.exists() and self.config_path == CONFIG_PATH.absolute():
            # Create default config file automatically
            self.generate_default_config()

    def __repr__(self) -> str:
        return f"ConfigLoader({self.config_path})"

    def _init_default_modules(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        config_dict.setdefault("tracer", {})
        config_dict.setdefault("collector", {})
        config_dict.setdefault("filter", {})
        config_dict.setdefault("monitor", {})
        return config_dict

    def generate_config(self):
        logger.info(f"Creating default config file {self.config_path}")
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(DEFAULT_CONFIG, self.config_path)

    def load_config(self) -> Dict[str, Any]:
        logger.info(f"Loading config from {self.config_path}")
        if not self.config_path.exists():
            raise ConfigFileNotFoundError(f"Config file:{self.config_path} not found.")

        try:
            with self.config_path.open("rb") as f:
                config = tomli.load(f)
                config = self._init_default_modules(config)
                return config
        except tomli.TOMLDecodeError as e:
            logger.error(f"Error loading config: {e}")
            raise e


class Configuable:
    default_config = {}
    config_scope: Optional[str] = None

    def __init__(self, config: Optional[Union[Config, Dict[str, Any]]] = None, *args, **kwargs):
        if not config:
            config = {}
        elif isinstance(config, Config):
            config = config.config_dict

        if self.config_scope:
            for score in self.config_scope.split("."):
                config = config.get(score, {})
        c = self.default_config.copy()
        c.update(config)
        self.config = Config(c)
        logger.debug(f"{self} config loaded.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.config})"
