import sys
from typing import Any, Dict, List, Optional

import pluggy

import duetector.analyzer.register
from duetector.analyzer.base import Analyzer
from duetector.extension.analyzer import project_name
from duetector.log import logger
from duetector.managers.base import Manager

PROJECT_NAME = project_name  #: Default project name for pluggy
hookspec = pluggy.HookspecMarker(PROJECT_NAME)


@hookspec
def init_analyzer(config) -> Optional[Analyzer]:
    """
    Initialize analyzer from config
    None means the analyzer is not available
    Also the analyzer can be disabled by config, Manager will discard disabled analyzer
    """


class AnalyzerManager(Manager):
    """
    Manager for all analyzers.

    Analyzers are initialized from config, and can be ``disabled`` by config.
    """

    config_scope = "analyzer"
    """
    Config scope for ``AnalyzerManager``.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.pm = pluggy.PluginManager(PROJECT_NAME)
        self.pm.add_hookspecs(sys.modules[__name__])
        self.pm.load_setuptools_entrypoints(PROJECT_NAME)
        self.register(duetector.analyzer.register)

    def init(self, analyzer_type=Analyzer, ignore_disabled=True) -> List[Analyzer]:
        """
        Initialize all analyzers from config.

        Args:
            analyzer_type: Only return analyzers of this type
            ignore_disabled: Ignore disabled analyzers
        """
        if self.disabled:
            logger.info("AnalyzerManager disabled.")
            return []

        objs = []
        for f in self.pm.hook.init_analyzer(config=self.config._config_dict):
            if not f or (f.disabled and ignore_disabled):
                logger.debug(f"Analyzer {f.__class__.__name__} is not available (None or Disabled)")
                continue
            if not isinstance(f, analyzer_type):
                logger.debug(
                    f"Skip Analyzer {f.__class__.__name__} (Not a instance of {analyzer_type})"
                )
                continue

            objs.append(f)

        return objs
