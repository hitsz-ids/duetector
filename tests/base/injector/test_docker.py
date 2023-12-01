import glob
import time
from collections import namedtuple
from pathlib import Path

import pytest

import docker
from duetector.injectors.docker import DockerInjector


@pytest.fixture(scope="session")
def command():
    return "sleep 181"


@pytest.fixture(scope="session")
def docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except:
        pytest.skip("Docker is not available")


@pytest.fixture(scope="session")
def test_container(docker_client: docker.DockerClient, command: str):
    try:
        """
        docker run --rm -d \
            ubuntu \
            sleep 181
        """
        container = docker_client.containers.run(
            "ubuntu",
            command=command.split(" "),
            detach=True,
            remove=True,
        )
        container.reload()
        while container.status != "running":
            container.reload()
            time.sleep(0.5)

        pid = None
        for p in glob.glob("/proc/[0-9]*"):
            p = Path(p)
            try:
                if (p / "cmdline").read_text().replace("\x00", " ").strip() == command.strip():
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

        yield container.attrs["Id"], int(pid)

    finally:
        container.stop()


@pytest.fixture(scope="session")
def docker_injector():
    d = DockerInjector()
    yield d
    d.shutdown()


def test_docker_inspect(test_container, docker_injector: DockerInjector):
    container_id, pid = test_container
    model = {
        "pid": pid,
    }
    data_t = namedtuple("T", ("pid",))

    patch_args = docker_injector.get_patch_kwargs(data_t(**model))
    assert docker_injector.is_inspected(patch_args)
    assert (
        docker_injector.get(patch_args, "container_id") == container_id
        or docker_injector.get(patch_args, "maybe_container_id") == container_id
    )


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
