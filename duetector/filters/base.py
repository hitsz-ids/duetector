import os
from typing import NamedTuple, Optional

from duetector.config import Configuable
from duetector.extension.filter import hookimpl


class Filter(Configuable):
    """
    A base class for all filters.

    Default config scope is ``filter.{class_name}``.

    subclass should override ``filter`` method.

    User should call Filter() directly to filter data,

    Example:

        .. code-block:: python

                from duetector.filters import Filter
                from duetector.collectors.models import Tracking

                class MyFilter(Filter):
                    def filter(self, data: Tracking) -> Optional[Tracking]:
                        if data.fname == "/etc/passwd":
                            return None
                        return data

                f = MyFilter()
                f(Tracking(fname="/etc/passwd"))  # None
                f(Tracking(fname="/etc/shadow"))  # Tracking(fname="/etc/shadow")
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for ``Filter``.
    """

    @property
    def config_scope(self):
        """
        Config scope for current filter.
        """
        return self.__class__.__name__

    @property
    def disabled(self):
        """
        If current filter is disabled.
        """
        return self.config.disabled

    def filter(self, data: NamedTuple) -> Optional[NamedTuple]:
        """
        Filter data, return ``None`` to drop data, return data to keep data.
        """
        raise NotImplementedError

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        if self.disabled:
            return data
        return self.filter(data)
