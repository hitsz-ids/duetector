import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.filters
from duetector.extension.filter import project_name
from duetector.filters.base import Filter
from duetector.log import logger
from duetector.manager import Manager

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_filter(config) -> Optional[Filter]:
    """
    Initialize filter from config
    None means the filter is not available
    Also the filter can be disabled by config, Manager will discard disabled filter
    """


class FilterManager(Manager):
    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.filters)

    def init(self) -> List[Filter]:
        objs = []
        for f in self.pm.hook.init_filter(config=self.config.config_dict):
            if isinstance(f, Filter) and not f.disabled:
                objs.append(f)
            else:
                logger.debug(
                    f"Collector {f.__class__.__name__} is not available (Not a instance of Collector or Disabled)"
                )

        return objs
