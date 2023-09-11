from typing import Any, Dict, Optional

from duetector.analyzer.base import Analyzer
from duetector.collectors.db import DBCollector
from duetector.db import SessionManager


class DBAnalyzer(Analyzer):
    """
    A analyzer using database.
    """

    default_config = {
        **Analyzer.default_config,
        "db": {**DBCollector.default_config.get("db", {})},
    }

    config_scope = "db_analyzer"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel
        self.sm = SessionManager(self.config._config_dict)
