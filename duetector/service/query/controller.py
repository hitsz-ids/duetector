from typing import Any, Dict, Optional

from duetector.analyzer.base import Analyzer
from duetector.analyzer.db import DBAnalyzer
from duetector.service.base import Controller


class AnalyzerController(Controller):
    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        # TODO: Make this configurable
        self.analyzer: Analyzer = self._init_analyzer(DBAnalyzer)

    def _init_analyzer(self, analyzer: type):
        analyzer_config = getattr(self.config, analyzer.config_scope)._config_dict
        return analyzer(analyzer_config)
