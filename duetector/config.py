import copy
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union

import tomli
import tomli_w

from duetector.exceptions import ConfigFileNotFoundError
from duetector.log import logger

_HERE = Path(__file__).parent
DEFAULT_CONFIG = _HERE / "static" / "config.toml"
CONFIG_PATH = "~/.config/duetector/config.toml"


class Config:
    """
    A wrapper for config dict

    All config keys are lower case.

    Access config by ``config.key`` and get all config by ``config._config_dict``.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        if not config_dict:
            config_dict = {}
        self._config_dict: Dict[str, Any] = config_dict

    def __repr__(self) -> str:
        return str(self._config_dict)

    def __getattr__(self, name):
        # All config keys are lower case
        name = name.lower()
        if isinstance(self._config_dict.get(name), dict):
            return Config(self._config_dict[name])

        return self._config_dict.get(name, None)

    def __bool__(self):
        return bool(self._config_dict)


class ConfigLoader:
    """
    A loader for config file and environment variables.

    Attributes:
        config_path (Path): Path to config file.
        load_env (bool): Load environment variables or not.
        dump_when_load (bool): Dump current config to a tmp file when load config.
        config_dump_dir (str): Directory to dump config.
        generate_config (bool): Generate config file if not exists.
    """

    ENV_PREFIX = "DUETECTOR_"
    ENV_SEP = "__"
    DUMP_DIR = "/tmp"

    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        load_env: bool = True,
        dump_when_load=True,
        config_dump_dir=None,
        generate_config=True,
    ):
        if not path:
            path = Path(CONFIG_PATH).expanduser()

        self.config_path: Path = Path(path).expanduser().absolute()
        if generate_config and not self.config_path.exists():
            self.generate_config()

        self.load_env = load_env
        self.dump_when_load = dump_when_load
        self.config_dump_dir = config_dump_dir or self.DUMP_DIR

    def __repr__(self) -> str:
        return f"ConfigLoader(path={self.config_path}, dump_when_load={self.dump_when_load}, load_env={self.load_env}, config_dump_dir={self.config_dump_dir})"

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

    def normalize_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make sure all config keys are lower case.
        """
        for k in list(config_dict.keys()):
            v = config_dict[k]
            if isinstance(v, dict):
                config_dict[k] = self.normalize_config(v)
            if k.lower() != k:
                config_dict[k.lower()] = config_dict.pop(k)

        return config_dict

    def load_config(self) -> Dict[str, Any]:
        """
        Load config from config file and environment variables.
        """
        logger.info(f"Loading config from {self.config_path}")
        if not self.config_path.exists():
            raise ConfigFileNotFoundError(f"Config file:{self.config_path} not found.")

        try:
            with self.config_path.open("rb") as f:
                config = tomli.load(f)

                config = self._init_default_modules(config)
                if self.load_env:
                    config = self.load_env_config(config)

                config = self.normalize_config(config)

                if self.dump_when_load:
                    # Dump current config to a tmp file
                    config_dump_path = (
                        Path(self.config_dump_dir) / f"duetector_config.toml.{os.getpid()}"
                    )
                    self.dump_config(config, config_dump_path)
                return config
        except tomli.TOMLDecodeError as e:
            logger.error(f"Error loading config: {e}")
            raise e

    def load_env_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load config from environment variables.

        Called by ``load_config``.
        """
        logger.info(
            f"Loading config from environment variables, prefix: `{self.ENV_PREFIX}`, sep: `{self.ENV_SEP}`"
        )
        for k, v in os.environ.items():
            if not k.startswith(self.ENV_PREFIX):
                continue
            k = k[len(self.ENV_PREFIX) :]
            k = k.lower()
            logger.debug(f"Loading {k.replace(self.ENV_SEP, '.')}={v}")
            *index, spec = k.split(self.ENV_SEP)
            last = config_dict
            for i in index:
                last = last.setdefault(i, {})
            last[spec] = v
        return config_dict

    def dump_config(self, config_dict: Dict[str, Any], path: Union[str, Path]):
        """
        Dump config to a file.
        """

        dump_path = Path(path).expanduser().resolve()
        dump_path.parent.mkdir(parents=True, exist_ok=True)
        with dump_path.open("wb") as f:
            tomli_w.dump(config_dict, f)
        logger.info(f"Current config has been dumped to {dump_path}")


class Configuable:
    """
    A base class for all configuable classes.

    It's recommended to use CLI to generate config file as ``config_scope`` may be masked ``manager``.

    Attributes:
        default_config (Dict[str, Any]): default config for this class
        config_scope (str): config scope for this class, e.g. ``tracer``, ``collector``
    """

    default_config = {}
    config_scope: Optional[str] = None

    def __init__(self, config: Optional[Union[Config, Dict[str, Any]]] = None, *args, **kwargs):
        if not config:
            config = {}
        elif isinstance(config, Config):
            config = config._config_dict

        if self.config_scope:
            for scope in self.config_scope.split("."):
                config = config.get(scope.lower(), {})
        c = copy.deepcopy(self.default_config)

        def _recursive_update(c, config):
            for k, v in config.items():
                if not isinstance(v, dict):
                    c[k] = v
                else:
                    c.setdefault(k, {})
                    _recursive_update(c[k], v)

        _recursive_update(c, config)
        self.config = Config(c)
        logger.debug(f"{self.__class__.__name__} config loaded.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.config})"
