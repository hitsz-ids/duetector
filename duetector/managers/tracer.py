import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.tracers.register
from duetector.extension.tracer import project_name
from duetector.log import logger
from duetector.managers.base import Manager
from duetector.tracers.base import Tracer

PROJECT_NAME = project_name  #: Default project name for pluggy
hookspec = pluggy.HookspecMarker(PROJECT_NAME)


@hookspec
def init_tracer(config) -> Optional[Tracer]:
    """
    Initialize tracer from config
    None means the tracer is not available
    Also the tracer can be disabled by config, Manager will discard disabled tracer
    """


class TracerManager(Manager):
    """
    Manager for all tracers.

    Tracers are initialized from config, and can be ``disabled`` by config.
    """

    config_scope = "tracer"
    """
    Config scope for ``TracerManager``.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(PROJECT_NAME)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(PROJECT_NAME)
        self.register(duetector.tracers.register)

    def init(self, tracer_type=Tracer, ignore_disabled=True) -> List[Tracer]:
        """
        Initialize all tracers from config.

        Args:
            tracer_type: Only return tracers of this type
            ignore_disabled: Ignore disabled tracers
        """
        if self.disabled:
            logger.info("TracerManager disabled.")
            return []

        objs = []
        for f in self.pm.hook.init_tracer(config=self.config._config_dict):
            if not f or (f.disabled and ignore_disabled):
                logger.debug(f"Tracer {f.__class__.__name__} is not available (None or Disabled)")
                continue
            if not isinstance(f, tracer_type):
                logger.debug(
                    f"Skip Tracer {f.__class__.__name__} (Not a instance of {tracer_type})"
                )
                continue

            objs.append(f)

        return objs
