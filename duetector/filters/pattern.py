import os
import re
from ast import literal_eval
from typing import List, NamedTuple, Optional, Set, Union

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

    Note:
        - We using python literal to parse config, so you can use environment variable to pass list:
            - Recommended: ``{PREFIX...}RE_EXCLUDE_FNAME="['/proc*', '/sys*']"``.
            - Remember to quote the value, otherwise it will be parsed as a expression, e.g. ``{PREFIX...}RE_EXCLUDE_FNAME=[/proc*]`` will cause SyntaxError or ValueError.
              and will fallback to split by comma.
        So either use python literal or string split by comma:
            - Recommended: ``{PREFIX...}RE_EXCLUDE_FNAME="['/proc*', '/sys*']"``
            - It's OK: ``{PREFIX...}RE_EXCLUDE_FNAME="/proc*, /sys*"``
            - Wrong: ``{PREFIX...}RE_EXCLUDE_FNAME=[/proc*, /sys*]``, this will be converted to a list of ``"[/proc*"`` and ``"/sys*]"``.

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

    @staticmethod
    def _wrap_exclude_list(value: Union[str, List[str]]) -> Set[str]:
        """
        Wrap exclude list to list if it's not a list
        """
        if isinstance(value, list):
            return set(str(v).strip() for v in value)
        if not isinstance(value, str):
            raise TypeError(f"Type of {value} should be str or list, got {type(value)}")

        try:
            # Use ast.literal_eval to parse python literal
            value = literal_eval(value)
        except (SyntaxError, ValueError):
            # If value is not a valid python literal, fallback to split by comma
            # e.g. "/proc/a*"
            value = value.split(",")

        try:
            return set(str(v).strip() for v in value)
        except TypeError:
            return set(str(value).strip())

    def is_exclude(self, data: NamedTuple, enable_customize_exclude=False) -> bool:
        """
        Customize exclude function, return ``True`` to drop data, return ``False`` to keep data.
        """
        for k in self.config._config_dict:
            if not enable_customize_exclude and k not in self.default_config:
                # If not enable_customize_exclude, only use default config
                continue

            if k.startswith("exclude_"):
                field = k.replace("exclude_", "")
                value = getattr(data, field, None)
                if value is None:
                    continue

                if str(value).strip() in self._wrap_exclude_list(self.config._config_dict[k]):
                    return True
            if k.startswith("re_exclude_"):
                field = k.replace("re_exclude_", "")
                value = getattr(data, field, None)
                if value is None:
                    continue
                if self.re_exclude(
                    str(value).strip(),
                    self._wrap_exclude_list(self.config._config_dict[k]),
                ):
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

        if self.is_exclude(data, enable_customize_exclude=self.enable_customize_exclude):
            return

        return data


@hookimpl
def init_filter(config=None):
    return PatternFilter(config=config)
