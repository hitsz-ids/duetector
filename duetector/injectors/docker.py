from __future__ import annotations

from collections import namedtuple
from typing import Any

import docker
from duetector.extension.injector import hookimpl
from duetector.injectors.base import ProcInjector
from duetector.injectors.inspector import Inspector


class DockerInjector(ProcInjector, Inspector):
    name = "docker"

    def __init__(self, config: dict[str, Any] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        try:
            self.client = docker.APIClient()
            if not self.client.ping():
                self.client = None
        except Exception:
            self.client = None

    def get_patch_kwargs(
        self, data: namedtuple, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not extra:
            extra = {}

        super_patch_kwargs = super().get_patch_kwargs(data, extra)

        extra.update(super_patch_kwargs)
        param = self.as_dict(data, extra)
        return {
            **super_patch_kwargs,
            **self.inspect(param),
        }

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        cgroups: list[str] | None = self.cgroup_inspector.get(model, "cgroups")
        if not cgroups:
            return {}
        container_id = None
        for cg in cgroups:
            if "docker" in cg:
                container_id = cg.split(":")[-1].split("/")[-1].lstrip("docker-").split(".")[0]
                break
        if not container_id:
            return {}

        if not self.client:
            return {"container_id": container_id}
        try:
            container_info = self.client.inspect_container(container_id)
        except Exception as e:
            pass

        return {
            "container_id": container_id,
        }


@hookimpl
def init_injector(config=None):
    return DockerInjector(config=config)
