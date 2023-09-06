import os
import re
from typing import List, NamedTuple, Optional, Union

from duetector.extension.filter import hookimpl
from duetector.filters import Filter


class PatternFilter(Filter):
    """
    A Filter support regex pattern to filter data.

    There are following config build-in:
            - ``re_exclude_fname``: Regex pattern to filter out ``fname`` field
            - ``re_exclude_comm``: Regex pattern to filter out ``comm`` field
            - ``exclude_pid``: Filter out ``pid`` field
            - ``exclude_uid``: Filter out ``uid`` field
            - ``exclude_gid``: Filter out ``gid`` field

    Customize exclude is also supported:
        - ``re_exclude_custom``: Regex pattern to filter out ``custom`` field
        - ``exclude_custom``: Filter out ``custom`` field

        You can change ``custom`` to any field you want to filter out.

        Config ``enable_customize_exclude`` to enable customize exclude, default is ``True``.

    Use ``(?!…)`` for include pattern:
        - ``re_exclude_custom``: ``["(?!/proc/)"]`` will include ``/proc`` but exclude others.
    """

    default_config = {
        **Filter.default_config,
        "enable_customize_exclude": True,
        "re_exclude_fname": [
            "/proc",
            "/sys",
            "/lib",
            "/dev",
            "/run",
            "/usr/lib",
            "/etc/ld.so.cache",
        ],
        "re_exclude_comm": [],
        "exclude_pid": [],
        "exclude_uid": [
            0,
        ],
        "exclude_gid": [
            0,
        ],
    }
    """
    Default config for ``PatternFilter``
    """
    _re_cache = {}
    """
    Cache for re pattern
    """

    @property
    def enable_customize_exclude(self) -> bool:
        """
        If enable customize exclude
        """
        return bool(self.config.enable_customize_exclude)

    def customize_exclude(self, data: NamedTuple) -> bool:
        """
        Customize exclude function, return ``True`` to drop data, return ``False`` to keep data.
        """
        for k in self.config._config_dict:
            if k.startswith("exclude_"):
                field = k.replace("exclude_", "")
                if getattr(data, field, None) in self.config._config_dict[k]:
                    return True
            if k.startswith("re_exclude_"):
                field = k.replace("re_exclude_", "")
                if self.re_exclude(getattr(data, field, None), self.config._config_dict[k]):
                    return True
        return False

    def re_exclude(self, field: Optional[str], re_list: Union[str, List[str]]) -> bool:
        """
        Check if field match any pattern in re_list
        """
        if not field:
            return False
        if isinstance(re_list, str):
            re_list = [re_list]

        def _cached_search(pattern, field):
            if pattern not in self._re_cache:
                self._re_cache[pattern] = re.compile(pattern)
            return self._re_cache[pattern].search(field)

        return any(_cached_search(pattern, field) for pattern in re_list)

    def filter(self, data: NamedTuple) -> Optional[NamedTuple]:
        """
        Filter data, return ``None`` to drop data, return data to keep data.
        """

        if getattr(data, "pid", None) == os.getpid():
            return
        if self.re_exclude(getattr(data, "fname", None), self.config.re_exclude_fname):
            return
        if self.re_exclude(getattr(data, "comm", None), self.config.re_exclude_comm):
            return

        if getattr(data, "pid", None) in self.config.exclude_pid:
            return
        if getattr(data, "uid", None) in self.config.exclude_uid:
            return
        if getattr(data, "gid", None) in self.config.exclude_gid:
            return

        if self.enable_customize_exclude and self.customize_exclude(data):
            return

        return data


@hookimpl
def init_filter(config=None):
    return PatternFilter(config=config)
