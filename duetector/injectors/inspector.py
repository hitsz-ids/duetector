from __future__ import annotations

from typing import Any

from duetector.utils import Singleton


class ProcWatcher(metaclass=Singleton):
    def __init__(self) -> None:
        pass


class Inspector:
    @property
    def id(self) -> str:
        return f"duetector_inspector_{self.__class__.__name__}".lower()

    def is_inspected(self, model: dict[str, Any]):
        return self.id in model and model[self.id]

    def mark_inspected(self, model: dict[str, Any]) -> None:
        model[self.id] = True

    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        if self.is_inspected(model):
            return {}

        inspect_info = self._inspect(model)
        self.mark_inspected(inspect_info)

        return inspect_info

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class NamespaceInspector(Inspector):
    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}


class CgroupInspector(Inspector):
    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}
