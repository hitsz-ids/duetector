import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.tracers
from duetector.extension.tracer import project_name
from duetector.log import logger
from duetector.manager import Manager
from duetector.tracers.base import Tracer

hookspec = pluggy.HookspecMarker(project_name)


@hookspec
def init_tracer(config) -> Optional[Tracer]:
    """
    Initialize tracer from config
    None means the tracer is not available
    Also the tracer can be disabled by config, Manager will discard disabled tracer
    """


class TracerManager(Manager):
    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(project_name)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(project_name)
        self.register(duetector.tracers)

    def init(self) -> List[Tracer]:
        objs = []
        for f in self.pm.hook.init_tracer(config=self.config.config_dict):
            if isinstance(f, Tracer) and not f.disabled:
                objs.append(f)
            else:
                logger.debug(
                    f"Collector {f.__class__.__name__} is not available (Not a instance of Collector or Disabled)"
                )

        return objs
