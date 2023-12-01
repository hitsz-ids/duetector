from __future__ import annotations

import os
from collections import namedtuple
from typing import Any

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache


import docker
from duetector.extension.injector import hookimpl
from duetector.injectors.base import ProcInjector
from duetector.injectors.inspector import Inspector
from duetector.log import logger


class DockerInjector(ProcInjector, Inspector):
    name = "docker"

    def __init__(self, config: dict[str, Any] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        try:
            # TODO: Config docker base_url and tls
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
        maybe_container_id = None
        try:
            for cg in cgroups:
                # FIXME: Need a more compatible way to get container_id
                maybe_container_id = (
                    cg.split(":")[-1].split("/")[-1].replace("docker-", "").split(".")[0]
                )
                break

        except IndexError:
            logger.info("Cann't parse container id.")
            logger.debug(f"{cgroups}")
            return {}
        if not maybe_container_id:
            return {}

        if not self.client:
            return {"maybe_container_id": maybe_container_id}

        container_info = {}
        try:
            container_info = self._query_container_info(maybe_container_id)
        except Exception as e:
            if "docker" not in cgroups[0]:
                return {"maybe_container_id": maybe_container_id}
            else:
                return {"container_id": maybe_container_id}

        return {
            "container_id": maybe_container_id,
            **container_info,
        }

    def _query_container_info(self, container_id: str) -> dict[str, Any]:
        # TODO: More info from container_info
        container_inspect = self.client.inspect_container(container_id)
        return {}


@hookimpl
def init_injector(config=None):
    return DockerInjector(config=config)


if __name__ == "__main__":
    pid = 1
    i = DockerInjector()
    model = {
        "pid": pid,
    }
    data_t = namedtuple("T", ("pid",))
    print(i.get_patch_kwargs(data_t(**model)))
    i.shutdown()
