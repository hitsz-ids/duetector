from __future__ import annotations

import copy
from collections import namedtuple
from typing import Any

from duetector.config import Configuable
from duetector.injectors.inspector import CgroupInspector, NamespaceInspector


class Injector(Configuable):
    """
    A base class for all Injectors.

    Default config scope is ``Injector.{class_name}``.

    subclass should override ``get_patch_kwargs`` method and ``super`` it for parent's patch kwargs.

    User should call Injector() directly to Injector data,
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for ``Injector``.
    """

    def __init__(self, config: dict[str, Any] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

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

    def get_patch_kwargs(
        self, data: namedtuple, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError

    def as_dict(self, data: namedtuple, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        if not extra:
            extra = {}
        param = data._asdict()
        for k, v in extra.items():
            param.setdefault(k, v)
        return param

    @staticmethod
    def patch(data: namedtuple, patch_kwargs: dict[str, Any]) -> namedtuple:
        fields = set(data._fields + tuple(patch_kwargs.keys()))
        new_data_t = namedtuple(data.__class__.__name__, fields)
        param: dict = data._asdict()
        for k, v in patch_kwargs.items():
            param.setdefault(k, v)
        return new_data_t(**param)

    def inject(self, data: namedtuple) -> namedtuple:
        return self.patch(data, self.get_patch_kwargs(data))

    def __call__(self, data: namedtuple) -> namedtuple | None:
        if self.disabled:
            return data
        return self.inject(data)

    def shutdown(self):
        pass


class ProcInjector(Injector):
    def __init__(self, config: dict[str, Any] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.cgroup_inspector = CgroupInspector()
        self.namespace_inspector = NamespaceInspector()

    def get_patch_kwargs(
        self, data: namedtuple, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        param = self.as_dict(data, extra)
        return {
            **self.cgroup_inspector.inspect(param),
            **self.namespace_inspector.inspect(param),
        }

    def shutdown(self):
        self.cgroup_inspector.stop()
        self.namespace_inspector.stop()
