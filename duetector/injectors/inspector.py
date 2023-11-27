from __future__ import annotations

from collections import namedtuple
from typing import Any

from duetector.utils import Singleton


class Inspector:
    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        raise NotImplemented


class NamespaceInspector(Inspector, metaclass=Singleton):
    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}


class CgroupInspector(Inspector, metaclass=Singleton):
    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}
