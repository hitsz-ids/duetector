import sys
from typing import List, Optional

import pluggy

import duetector.tracers
from duetector.extension.tracer import project_name
from duetector.manager import Manager
from duetector.tracers.base import Tracer

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_tracer(config) -> Optional[Tracer]:
    """Initialize tracer from config"""


class TracerManager(Manager):
    def __init__(self, config=None):
        self.config = config

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.tracers)

    def init(self) -> List[Tracer]:
        objs = []
        for f in self.pm.hook.init_tracer(config=self.config):
            if f is not None:
                objs.append(f)

        return objs
