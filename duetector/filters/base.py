import os
from typing import NamedTuple, Optional

from duetector.extension.filter import hookimpl


class Filter:
    def __init__(self, config=None):
        # TODO: Dependency injection for config
        self.config = config

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
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
    return Filter(config=config)
