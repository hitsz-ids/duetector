import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.filters
from duetector.extension.filter import project_name
from duetector.filters.base import Filter
from duetector.log import logger
from duetector.managers import Manager

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_filter(config) -> Optional[Filter]:
    """
    Initialize filter from config
    None means the filter is not available
    Also the filter can be disabled by config, Manager will discard disabled filter
    """


class FilterManager(Manager):
    config_scope = "filter"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.filters)

    def init(self, ignore_disabled=True) -> List[Filter]:
        if self.disabled:
            logger.info("FilterManager disabled.")
            return []
        objs = []
        for f in self.pm.hook.init_filter(config=self.config.config_dict):
            if not f:
                continue
            if f.disabled and ignore_disabled:
                logger.info(f"Filter {f.__class__.__name__} is disabled")
                continue

            objs.append(f)

        return objs
