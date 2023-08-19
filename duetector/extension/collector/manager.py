import sys
from typing import List, Optional

import pluggy

import duetector.collectors
from duetector.collectors.base import Collector

from .var import project_name

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_collector(config) -> Optional[Collector]:
    """Initialize tracer from config"""


class CollectorManager:
    def __init__(self, config=None):
        self.config = config

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.collectors)

    def register(self, module):
        self.pm.register(module)

    def init(self) -> List[Collector]:
        objs = []
        for f in self.pm.hook.init_collector(config=self.config):
            if f is not None:
                objs.append(f)

        return objs
