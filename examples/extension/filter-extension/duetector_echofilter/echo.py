from typing import NamedTuple, Optional

from duetector.extension.filter import hookimpl
from duetector.filters import Filter


class EchoFilter(Filter):
    default_config = {
        **Filter.default_config,  # inherit default_config
        "disabled": False,
    }

    def __call__(self, data: NamedTuple) -> Optional[NamedTuple]:
        print(data)
        return data


@hookimpl
def init_filter(config):
    return EchoFilter(config)
