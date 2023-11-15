import socket
import time
from collections import namedtuple

import httpx
import pytest

import docker
from duetector.analyzer.jaeger.analyzer import JaegerAnalyzer
from duetector.collectors.otel import OTelCollector


def get_port():
    # Get an unoccupied port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


from duetector.utils import get_boot_time_duration_ns

timestamp = 13205215231927
datetime = get_boot_time_duration_ns(timestamp)


@pytest.fixture(scope="session")
def data_t():
    d = namedtuple("Tracking", ["pid", "uid", "gid", "comm", "fname", "timestamp", "custom"])

    yield d(
        pid=9999,
        uid=9999,
        gid=9999,
        comm="dummy",
        fname="dummy.file",
        timestamp=timestamp,
        custom="dummy-xargs",
    )


@pytest.fixture(scope="session")
def service_id():
    yield "unittest-service"


@pytest.fixture(scope="session")
def docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except:
        pytest.skip("Docker is not available")


@pytest.fixture(scope="session")
def jaeger_container(docker_client: docker.DockerClient, service_id, data_t):
    query_port = get_port()
    otel_grpc_port = get_port()
    ui_port = get_port()
    try:
        """
        docker run --rm --name jaeger \
            -p {random_query_port}:16685 \
            -p {random_otel_port}:4317 \
            jaegertracing/all-in-one:1.50
        """
        container = docker_client.containers.run(
            "jaegertracing/all-in-one:1.50",
            detach=True,
            ports={"16685": query_port, "4317": otel_grpc_port, "16686": ui_port},
        )
        # Waiting for the container to start by query ui_port
        while True:
            try:
                response = httpx.get(f"http://127.0.0.1:{ui_port}")
                if response.status_code == 200:
                    break
            except:
                time.sleep(0.1)

        # Generate testing data
        config = {
            "otelcollector": {
                "disabled": False,
                "statis_id": service_id,
                "exporter": "otlp-grpc",
                "exporter_kwargs": {
                    "endpoint": f"127.0.0.1:{otel_grpc_port}",
                    "insecure": True,
                },
            }
        }
        collector = OTelCollector(config)
        collector.emit("dummy", data_t)
        collector.shutdown()

        yield query_port
    finally:
        container.stop()


@pytest.fixture
def jaeger_analyzer(jaeger_container):
    config = {
        "jaegeranalyzer": {
            "disabled": False,
            "host": "127.0.0.1",
            "port": jaeger_container,
        }
    }
    yield JaegerAnalyzer(config)


async def test_jaeger_analyzer(jaeger_analyzer: JaegerAnalyzer):
    from duetector.analyzer.jaeger.proto.query_pb2 import GetServicesRequest
    from duetector.analyzer.jaeger.proto.query_pb2_grpc import QueryServiceStub

    async with jaeger_analyzer.channel_initializer() as channel:
        stub = QueryServiceStub(channel)
        response = await stub.GetServices(GetServicesRequest())
        print(response)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
