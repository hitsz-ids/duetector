import os
from typing import NamedTuple, Optional

from duetector.config import Configuable
from duetector.extension.filter import hookimpl


class Filter(Configuable):
    default_config = {
        "disabled": False,
    }

    @property
    def config_scope(self):
        return self.__class__.__name__

    @property
    def disabled(self):
        return self.config.disabled

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        raise NotImplementedError


class DefaultFilter(Filter):
    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        if self.disabled:
            return data

        fname = getattr(data, "fname")
        if (
            fname
            and any(
                [
                    fname.startswith(p)
                    for p in [
                        "/proc",
                        "/sys",
                        "/lib",
                        "/dev",
                        "/run",
                        "/usr/lib",
                        "/etc/ld.so.cache",
                    ]
                ]
            )
            or getattr(data, "pid") == os.getpid()
        ):
            return None

        return data


@hookimpl
def init_filter(config=None):
    return DefaultFilter(config=config)
