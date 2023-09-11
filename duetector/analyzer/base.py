from typing import List

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
