import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.filters.register
from duetector.extension.filter import project_name
from duetector.filters.base import Filter
from duetector.log import logger
from duetector.managers.base import Manager

PROJECT_NAME = project_name  #: Default project name for pluggy
hookspec = pluggy.HookspecMarker(PROJECT_NAME)


@hookspec
def init_filter(config) -> Optional[Filter]:
    """
    Initialize filter from config
    None means the filter is not available
    Also the filter can be disabled by config, Manager will discard disabled filter
    """


class FilterManager(Manager):
    """
    Manager for all filters.

    Filters are initialized from config, and can be ``disabled`` by config.
    """

    config_scope = "filter"
    """
    Config scope for ``FilterManager``.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(PROJECT_NAME)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(PROJECT_NAME)
        self.register(duetector.filters.register)

    def init(self, ignore_disabled=True) -> List[Filter]:
        """
        Initialize all filters from config.

        Args:
            ignore_disabled: Ignore disabled filters
        """
        if self.disabled:
            logger.info("FilterManager disabled.")
            return []
        objs = []
        for f in self.pm.hook.init_filter(config=self.config._config_dict):
            if not f:
                continue
            if f.disabled and ignore_disabled:
                logger.info(f"Filter {f.__class__.__name__} is disabled")
                continue

            objs.append(f)

        return objs
