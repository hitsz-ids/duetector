from datetime import datetime
from typing import List, Optional

from duetector.analyzer.models import AnalyzerBrief, Tracking
from duetector.config import Configuable


class Analyzer(Configuable):
    """
    A base class for all analyzers.
    """

    default_config = {}
    """
    Default config for ``Analyzer``.
    """

    config_scope = "analyzer"
    """
    Config scope for this analyzer.

    Subclasses cloud override this.
    """

    def get_all_tracers(self) -> List[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """
        raise NotImplementedError

    def get_all_collector_ids(self) -> List[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        raise NotImplementedError

    def query(
        self,
        tracer: Optional[str] = None,
        collector_id: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start: int = 0,
        limit: int = 20,
    ) -> List[Tracking]:
        """
        Query tracking data from storage.
        """
        raise NotImplementedError

    def brief(
        self,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> AnalyzerBrief:
        """
        Get brief of analyzer.
        """
        raise NotImplementedError

    def analyze(self):
        # TODO: Not design yet.
        pass
