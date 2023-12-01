from __future__ import annotations

from collections import namedtuple
from typing import Any

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from kubernetes import client
from kubernetes import config as k8s_config

from duetector.extension.injector import hookimpl
from duetector.injectors.base import ProcInjector
from duetector.injectors.inspector import Inspector
from duetector.log import logger


class K8SInjector(ProcInjector, Inspector):
    name = "k8s"

    def __init__(self, config: dict[str, Any] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        try:
            try:
                # TODO: Config kube config path
                k8s_config.load_kube_config()
            except k8s_config.config_exception.ConfigException:
                k8s_config.load_incluster_config()
        except Exception:
            self.client = None
        else:
            self.client = client

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
        maybe_pod_id = None
        maybe_container_id = None
        try:
            for cg in cgroups:
                maybe_pod_id_str_list = cg.split(":")[-1].split("/")[-2].split(".")[0].split("-")
                for i, s in enumerate(maybe_pod_id_str_list):
                    if s.startswith("pod"):
                        maybe_pod_id_str_list[i] = maybe_pod_id_str_list[i].strip("pod")
                        maybe_pod_id = "-".join(maybe_pod_id_str_list[i:]).replace("_", "-")
                        break
                maybe_container_id = (
                    cg.split(":")[-1].split("/")[-1].replace("docker-", "").split(".")[0]
                )
                break
        except IndexError:
            logger.info("Cann't parse container id and pod id.")
            logger.debug(f"{cgroups}")
            return {}
        if not (maybe_pod_id and maybe_container_id):
            return {}

        container_info = self._query_container_info(maybe_pod_id, maybe_container_id)

        return {
            "pod_id": maybe_pod_id,
            "container_id": maybe_container_id,
            **container_info,
        }

    @cache
    def _query_container_info(self, pod_id: str, maybe_container_id: str):
        if not self.client:
            return {}
        pod = None
        container_status = None
        container_info = {}
        try:
            for p in self.client.CoreV1Api().list_pod_for_all_namespaces().items:
                if p.metadata.uid == pod_id:
                    pod = p
                    container_info["pod_name"] = p.metadata.name
                    container_info["namespace"] = p.metadata.namespace
                    break
            if not pod:
                logger.info(f"Pod not found: {pod_id}")
                return container_info
            for cs in pod.status.container_statuses:
                if maybe_container_id in cs.container_id:
                    container_status = cs
                    container_info["container_name"] = cs.name
                    container_info["container_runtime"] = cs.container_id.split(":")[0]
                    break
            if not container_status:
                logger.info(f"Container not found: {maybe_container_id}")
                return container_info

        except Exception as e:
            logger.error("Exception when query container info from k8s api.")
            logger.exception(e)
            return container_info

        return container_info


@hookimpl
def init_injector(config=None):
    return K8SInjector(config=config)


if __name__ == "__main__":
    pid = 105846
    i = K8SInjector()
    model = {
        "pid": pid,
    }
    data_t = namedtuple("T", ("pid",))
    print(i.get_patch_kwargs(data_t(**model)))
    i.shutdown()
