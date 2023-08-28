import os
import re
from typing import List, NamedTuple, Optional, Union

from duetector.extension.filter import hookimpl
from duetector.filters import Filter


class PatternFilter(Filter):
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
    _re_cache = {}

    @property
    def enable_customize_exclude(self) -> bool:
        return bool(self.config.enable_customize_exclude)

    def customize_exclude(self, data: NamedTuple) -> bool:
        for k in self.config.config_dict:
            if k.startswith("exclude_"):
                field = k.replace("exclude_", "")
                if getattr(data, field, None) in self.config.config_dict[k]:
                    return True
            if k.startswith("re_exclude_"):
                field = k.replace("re_exclude_", "")
                if self.re_exclude(getattr(data, field, None), self.config.config_dict[k]):
                    return True
        return False

    def re_exclude(self, field: Optional[str], re_list: Union[str, List[str]]) -> bool:
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
