import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.collectors
from duetector.collectors.base import Collector
from duetector.extension.collector import project_name
from duetector.log import logger
from duetector.managers import Manager

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_collector(config) -> Optional[Collector]:
    """
    Initialize collector from config
    None means the collector is not available
    Also the collector can be disabled by config, Manager will discard disabled collectors
    """


class CollectorManager(Manager):
    config_scope = "collector"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.collectors)

    def init(self, ignore_disabled=True) -> List[Collector]:
        if self.disabled:
            logger.info("CollectorManager disabled.")
            return []

        objs = []
        for f in self.pm.hook.init_collector(config=self.config.config_dict):
            if not f:
                continue
            if f.disabled and ignore_disabled:
                logger.info(f"Collector {f.__class__.__name__} is disabled")
                continue

            objs.append(f)

        return objs
