import pluggy

from duetector.config import Configuable


class Manager(Configuable):
    """
    Manager based on pulggy

    FIXME: Need better abstraction, lots of duplicated code in subclasses
    """

    pm: pluggy.PluginManager

    default_config = {"disabled": False}

    def register(self, subpackage):
        registers = getattr(subpackage, "registers", [subpackage])
        for register in registers:
            self.pm.register(register)

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled
