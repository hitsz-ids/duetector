from typing import Any, Dict, Optional

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

    default_config = {
        "disabled": False,
        "include_extension": True,
    }
    """
    Default config for ``Manager``
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        # Allow disable extensions when instantiate
        self._include_extension = kwargs.get("disable_extensions")

    @property
    def include_extension(self):
        """
        If include extensions
        """
        if self._include_extension is not None:
            return self._include_extension
        return self.config.include_extension

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
