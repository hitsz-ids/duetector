import sys
from typing import List, Optional

import pluggy

import duetector.filters
from duetector.extension.filter import project_name
from duetector.filters.base import Filter

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_filter(config) -> Optional[Filter]:
    """Initialize tracer from config"""


class FilterManager:
    def __init__(self, config=None):
        self.config = config

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.filters)

    def register(self, module):
        self.pm.register(module)

    def init(self) -> List[Filter]:
        objs = []
        for f in self.pm.hook.init_filter(config=self.config):
            if f is not None:
                objs.append(f)

        return objs
