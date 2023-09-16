from typing import Any, Dict, List, Optional

from duetector.analyzer.base import Analyzer
from duetector.managers.analyzer import AnalyzerManager
from duetector.service.base import Controller
from duetector.service.exceptions import NotFoundError


class AnalyzerController(Controller):
    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        # TODO: Make this configurable, may intro a manager for analyzer
        self._avaliable_analyzers = AnalyzerManager(config).init()

        self._analyzers: Dict[str, Analyzer] = {
            analyzer.config_scope: analyzer for analyzer in self._avaliable_analyzers
        }

    def _init_analyzer(self, analyzer: type):
        analyzer_config = getattr(self.config, analyzer.config_scope)._config_dict
        return analyzer(analyzer_config)

    @property
    def avaliable_analyzer_names(self) -> List[str]:
        return [a.config_scope for a in self._avaliable_analyzers]

    def get_analyzer(self, analyzer_name: str) -> Analyzer:
        """
        Get analyzer by name

        Args:
            analyzer_name (str): analyzer name, should be one of avaliable_analyzer_names

        Raises:
            NotFoundError: if analyzer not found

        Returns:
            Analyzer: analyzer instance

        Allow use "-" or "_" in analyzer name, for example, both "db-analyzer" and "db_analyzer" are ok.

        Examples:
            >>> controller.get_analyzer("db-analyzer")
        """
        a = self._analyzers.get(analyzer_name) or self._analyzers.get(
            analyzer_name.replace("-", "_")
        )
        if not a:
            raise NotFoundError(analyzer_name)
        return a
