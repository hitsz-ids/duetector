import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.collectors.register
from duetector.collectors.base import Collector
from duetector.extension.collector import project_name
from duetector.log import logger
from duetector.managers.base import Manager

PROJECT_NAME = project_name  #: Default project name for pluggy
hookspec = pluggy.HookspecMarker(PROJECT_NAME)


@hookspec
def init_collector(config) -> Optional[Collector]:
    """
    Initialize collector from config.

    None means the collector is not available.

    Also the collector can be ``disabled`` by config, Manager will discard disabled collectors.
    """


class CollectorManager(Manager):
    """
    Manager for all collectors.

    Collectors are initialized from config, and can be ``disabled`` by config.
    """

    config_scope = "collector"
    """
    Config scope for ``CollectorManager``.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(PROJECT_NAME)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(PROJECT_NAME)
        self.register(duetector.collectors.register)

    def init(self, ignore_disabled=True) -> List[Collector]:
        """
        Initialize all collectors from config.

        Args:
            ignore_disabled: Ignore disabled collectors
        """
        if self.disabled:
            logger.info("CollectorManager disabled.")
            return []

        objs = []
        for f in self.pm.hook.init_collector(config=self.config):
            if not f:
                continue
            if f.disabled and ignore_disabled:
                logger.info(f"Collector {f.__class__.__name__} is disabled")
                continue

            objs.append(f)

        return objs
