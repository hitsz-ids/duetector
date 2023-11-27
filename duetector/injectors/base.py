from __future__ import annotations

import os
from collections import namedtuple

from duetector.config import Configuable


class NamespaceMixin:
    pass


class CgroupMixin:
    pass


class Injector(Configuable):
    """
    A base class for all Injectors.

    Default config scope is ``Injector.{class_name}``.

    subclass should override ``inject`` method and ``super`` it.

    User should call Injector() directly to Injector data,
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for ``Injector``.
    """

    @property
    def config_scope(self):
        """
        Config scope for current Injector.
        """
        return self.__class__.__name__

    @property
    def disabled(self):
        """
        If current Injector is disabled.
        """
        return self.config.disabled

    def inject(self, data: namedtuple) -> namedtuple:
        """
        Implement this method to patch ``data``
        """
        return data

    def __call__(self, data: namedtuple) -> namedtuple | None:
        if self.disabled:
            return data
        return self.inject(data)
