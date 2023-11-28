from __future__ import annotations

import itertools
from typing import Any

from duetector.utils import Singleton


class ProcWatcher(metaclass=Singleton):
    def __init__(self) -> None:
        pass


def with_prefix(sep: str, prefix, key: str | list[str]) -> str:
    if isinstance(key, str):
        return sep.join([prefix, key.lower()])
    else:
        return sep.join(itertools.chain([prefix], [k.lower() for k in key]))


class Inspector:
    sep = "__"
    prefix = "inspector"
    name = None

    @property
    def id(self) -> str:
        return with_prefix(self.sep, self.prefix, self.name or self.__class__.__name__)

    def with_id(self, key: str | list[str]) -> str:
        return with_prefix(self.sep, self.id, key)

    def is_inspected(self, model: dict[str, Any]):
        return self.id in model and model[self.id]

    def _mark_inspected(self, model: dict[str, Any]) -> None:
        model[self.id] = True

    def _ensure_with_id(self, model: dict[str, Any]) -> dict[str, Any]:
        return {self.with_id(k) if not k.startswith(self.id) else k: v for k, v in model.items()}

    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        if self.is_inspected(model):
            return {}

        inspect_info = self._inspect(model)
        inspect_info = self._ensure_with_id(inspect_info)
        self._mark_inspected(inspect_info)

        return inspect_info

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class NamespaceInspector(Inspector):
    @property
    def name(self) -> str:
        return self.sep.join(["proc", "namespace"])

    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}


class CgroupInspector(Inspector):
    @property
    def name(self) -> str:
        return self.sep.join(["proc", "cgroup"])

    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}
