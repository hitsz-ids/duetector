import sys
from typing import List, Optional

import pluggy

import duetector.collectors
from duetector.collectors.base import Collector
from duetector.extension.collector import project_name
from duetector.manager import Manager

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_collector(config) -> Optional[Collector]:
    """Initialize tracer from config"""


class CollectorManager(Manager):
    def __init__(self, config=None):
        self.config = config

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.collectors)

    def init(self) -> List[Collector]:
        objs = []
        for f in self.pm.hook.init_collector(config=self.config):
            if f is not None:
                objs.append(f)

        return objs
