import pluggy

from duetector.config import Configuable


class Manager(Configuable):
    """
    Manager based on pulggy

    Default config scope is ``{class_name}``

    FIXME:
        Need better abstraction, lots of duplicated code in subclasses
    """

    pm: pluggy.PluginManager
    """
    PluginManager instance
    """

    default_config = {"disabled": False}
    """
    Default config for ``Manager``
    """

    def register(self, subpackage):
        """
        Register subpackage to plugin manager
        """
        registers = getattr(subpackage, "registers", [subpackage])
        for register in registers:
            self.pm.register(register)

    @property
    def config_scope(self):
        """
        Config scope for current manager.
        """
        return self.__class__.__name__

    @property
    def disabled(self):
        """
        If current manager is disabled.
        """
        return self.config.disabled
