from duetector.config import Configuable


class Analyzer(Configuable):
    """
    A base class for all analyzers.
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for ``Analyzer``.
    """

    config_scope = "analyzer"

    @property
    def disabled(self):
        """
        If current analyzer is disabled.
        """
        return self.config.disabled
