import sys
from typing import Any, Dict, Iterable, List, Optional, Union

import pluggy

import duetector.tracers.register
from duetector.config import Config, Configuable
from duetector.extension.tracer import project_name
from duetector.log import logger
from duetector.managers.base import Manager
from duetector.tracers.base import ShellTracer, SubprocessTracer, Tracer

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
    """
    Using template to generate tracers.

    Tracers are initialized from config, and can be ``disabled`` by config.
    Tracer type is defined by ``_avaliable_tracer_type``.


    Example:

    .. code-block:: toml

        [tracer.template.sh]
        pstracer = { "comm" = ["ps", "-aux"], config = { "enable_cache" = false } }

        [tracer.template.sp]
        randomtracer = { "comm" = ["cat", "/dev/random"], config = { "enable_cache" = false } }

    TODO:

    Example of ``tracer.template.sp`` is not working yet. Replace it with some CO-RE example

    """

    _avaliable_tracer_type = {
        "sh": ShellTracer,
        "sp": SubprocessTracer,
    }
    """
    Available tracer type.
    """

    default_config = {
        "disabled": False,
        **{k: dict() for k in _avaliable_tracer_type.keys()},
    }
    """
    Default config for ``TracerTemplate``.
    """

    @property
    def disabled(self) -> bool:
        """
        Whether the template is disabled.
        """
        return self.config.disabled

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    def _get_wrap_tracer(
        self, tracer_type: Union[str, type], tracer_name: str, kwargs: Config
    ) -> Tracer:
        """
        Get a wrapper class for tracer type.
        """
        if isinstance(tracer_type, str):
            tracer_type = self._avaliable_tracer_type[tracer_type]

        class WrapTracer(tracer_type):
            config_scope = None

        tracer_config = kwargs.pop("config", {})
        WrapTracer.__name__ = WrapTracer.name = tracer_name
        for k, v in kwargs.items():
            setattr(WrapTracer, k, v)

        return WrapTracer(tracer_config)

    def init(self) -> List[Tracer]:
        """
        Initialize all tracers from config.
        """
        if self.disabled:
            logger.info("TracerTemplate disabled.")
            return []

        objs = []
        for k, tracer_type in self._avaliable_tracer_type.items():
            for tracer_name, kwargs in self.config._config_dict[k].items():
                objs.append(self._get_wrap_tracer(tracer_type, tracer_name, kwargs))

        return objs


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
