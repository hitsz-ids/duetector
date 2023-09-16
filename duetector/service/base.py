from typing import Any, Dict, Optional

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from fastapi import Depends

from duetector.config import Configuable
from duetector.service.config import get_config


class Controller(Configuable):
    config_scope = None

    default_config = {}

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)


@cache
def get_controller(controller_type: type):
    def _(config: dict = Depends(get_config)) -> Controller:
        return controller_type(config)

    return _
