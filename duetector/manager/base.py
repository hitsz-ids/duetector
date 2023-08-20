import pluggy


class Manager:
    pm: pluggy.PluginManager

    def register(self, subpackage):
        registers = getattr(subpackage, "registers", [subpackage])
        for register in registers:
            self.pm.register(register)
