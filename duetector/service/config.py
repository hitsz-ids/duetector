import os
from typing import Any, Dict

from fastapi import Depends

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.config import Config, ConfigLoader, Configuable

CONFIG_PATH_ENV = "DUETECTOR_SERVER_CONFIG_PATH"


@cache
def get_config() -> Dict[str, Any]:
    config_path = os.environ.get(CONFIG_PATH_ENV)
    if config_path is None:
        raise RuntimeError(
            f"Environment variable {CONFIG_PATH_ENV} is not set. "
            f"Please set it to the path of the config file."
        )
    return ConfigLoader(
        path=config_path,
        load_env=False,
        dump_when_load=False,
    ).load_config()


class ServerConfig(Configuable):
    config_scope = "server"
    default_config = {"token": ""}


def get_server_config(
    config: Dict[str, Any] = Depends(get_config),
) -> Config:
    return ServerConfig(config).config
