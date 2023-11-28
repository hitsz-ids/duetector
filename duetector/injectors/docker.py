from collections import namedtuple
from typing import Any

from duetector.extension.injector import hookimpl
from duetector.injectors.base import ProcInjector


class DockerInjector(ProcInjector):
    def get_patch_kwargs(
        self, data: namedtuple, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        extra.update(super().get_patch_kwargs(data, extra))
        param = self.as_dict(data, extra)
        return {}


@hookimpl
def init_injector(config=None):
    return DockerInjector(config=config)
