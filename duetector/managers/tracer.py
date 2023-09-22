import sys
from typing import Any, Dict, Iterable, List, Optional, Union

import pluggy

import duetector.tracers.register
from duetector.config import Configuable
from duetector.extension.tracer import project_name
from duetector.log import logger
from duetector.managers.base import Manager
from duetector.tracers.base import ShellTracer, Tracer

PROJECT_NAME = project_name  #: Default project name for pluggy
hookspec = pluggy.HookspecMarker(PROJECT_NAME)


@hookspec
def init_tracer(config) -> Optional[Tracer]:
    """
    Initialize tracer from config
    None means the tracer is not available
    Also the tracer can be disabled by config, Manager will discard disabled tracer
    """


class TracerTemplate(Configuable):
    _avaliable_tracer_type = {
        "sh": ShellTracer,
    }

    default_config = {
        "disabled": False,
        **{k: dict() for k in _avaliable_tracer_type.keys()},
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self._avaliable_tracer: Dict[type, Dict[str, Any]] = {}

    def init(self) -> List[Tracer]:
        return []


class TracerManager(Manager):
    """
    Manager for all tracers.

    Tracers are initialized from config, and can be ``disabled`` by config.
    """

    default_config = {
        **Manager.default_config,
        "template": {**TracerTemplate.default_config},
    }

    config_scope = "tracer"
    """
    Config scope for ``TracerManager``.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(PROJECT_NAME)
        self.pm.add_hookspecs(sys.modules[__name__])
        if self.include_extension:
            self.pm.load_setuptools_entrypoints(PROJECT_NAME)
        self.register(duetector.tracers.register)

        self.template = TracerTemplate(self.config.template)

    def init(
        self,
        tracer_type=Tracer,
        ignore_disabled=True,
        include_template=True,
        *args,
        **kwargs,
    ) -> List[Tracer]:
        """
        Initialize all tracers from config.

        Args:
            tracer_type: Only return tracers of this type
            ignore_disabled: Ignore disabled tracers
            include_template: Include tracers from template, ``False`` when used to generate configuration.
        """
        if self.disabled:
            logger.info("TracerManager disabled.")
            return []

        objs = []
        tracers = list(self.pm.hook.init_tracer(config=self.config))
        if include_template:
            tracers.extend(self.template.init())

        for f in tracers:
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
