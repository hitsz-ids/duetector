import pluggy

from duetector.config import Configuable


class Manager(Configuable):
    pm: pluggy.PluginManager

    def register(self, subpackage):
        registers = getattr(subpackage, "registers", [subpackage])
        for register in registers:
            self.pm.register(register)

    @property
    def config_spec(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled
