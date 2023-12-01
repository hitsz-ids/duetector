from __future__ import annotations

from collections import namedtuple

from duetector.config import Configuable


class Filter(Configuable):
    """
    A base class for all filters.

    Default config scope is ``filter.{class_name}``.

    subclass should override ``filter`` method.

    User should call Filter() directly to filter data,

    Example:

        .. code-block:: python

                from duetector.filters import Filter
                from collections import namedtuple

                class MyFilter(Filter):
                    def filter(self, data: namedtuple) -> namedtuple | None:
                        if data.fname == "/etc/passwd":
                            return None
                        return data

                f = MyFilter()
                data_t = namedtuple("Tracking", "fname")
                f(data_t(fname="/etc/passwd"))  # None
                f(data_t(fname="/etc/shadow"))  # Tracking(fname="/etc/shadow")
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

    def filter(self, data: namedtuple) -> namedtuple | None:
        """
        Filter data, return ``None`` to drop data, return data to keep data.
        """
        raise NotImplementedError

    def __call__(self, data: namedtuple) -> namedtuple | None:
        if self.disabled:
            return data
        return self.filter(data)
