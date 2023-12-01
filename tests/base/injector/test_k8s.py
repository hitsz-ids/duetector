import glob
import time
from collections import namedtuple
from pathlib import Path

import pytest
import yaml
from kubernetes import client
from kubernetes import config as k8s_config

from duetector.injectors.docker import DockerInjector
from duetector.injectors.k8s import K8SInjector


@pytest.fixture(scope="session")
def k8s_client():
    try:
        try:
            k8s_config.load_kube_config()
        except k8s_config.config_exception.ConfigException:
            k8s_config.load_incluster_config()
    except Exception:
        pytest.skip("K8S Config not avaliable.")

    try:
        client.CoreV1Api().list_pod_for_all_namespaces()
    except Exception:
        pytest.skip("K8S API not avaliable.")

    return client


@pytest.fixture(scope="session")
def k8s_pod(k8s_client: client):
    pod_name = "testpod"
    container_name = "testcontainer"

    y = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
spec:
  containers:
  - name: {container_name}
    image: ubuntu
    command:
    - sleep
    - "181"
"""
    try:
        k8s_client.CoreV1Api().create_namespaced_pod(
            namespace="default",
            body=yaml.safe_load(y),
        )
    except Exception as e:
        pytest.skip("Unable to create k8s pod")
        # Wait for pod to be running
    try:
        while True:
            pod_status = k8s_client.CoreV1Api().read_namespaced_pod_status(
                name=pod_name, namespace="default"
            )
            if pod_status.status.phase == "Running":
                break
            time.sleep(1)

        for p in glob.glob("/proc/[0-9]*"):
            p = Path(p)
            try:
                if (p / "cmdline").read_text().replace("\x00", " ").strip() == "sleep 181".strip():
                    pid = p.name
                    try:
                        (p / "cgroup").read_text().strip().split("\n")
                    except PermissionError as e:
                        pytest.skip(
                            "Low privileges for the current user to inspect docker container's process"
                        )
            except FileNotFoundError as e:
                continue

        assert pid

        yield pod_name, container_name, pid

    finally:
        k8s_client.CoreV1Api().delete_namespaced_pod(
            name=pod_name,
            namespace="default",
            body=client.V1DeleteOptions(),
        )


@pytest.fixture
def k8s_injector():
    i = K8SInjector()
    try:
        yield i
    finally:
        i.shutdown()


def test_k8s_injector(k8s_pod, k8s_injector):
    pod_name, container_name, pid = k8s_pod
    model = {
        "pid": pid,
    }
    data_t = namedtuple("T", ("pid",))
    patch_args = k8s_injector.get_patch_kwargs(data_t(**model))
    assert k8s_injector.is_inspected(patch_args)
    assert k8s_injector.get(patch_args, "pod_name") == pod_name
    assert k8s_injector.get(patch_args, "namespace") == "default"
    assert k8s_injector.get(patch_args, "container_name") == container_name
    assert k8s_injector.get(patch_args, "container_runtime")


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
