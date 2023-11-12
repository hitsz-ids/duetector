import asyncio

import grpc

from duetector.analyzer.base import Analyzer
from duetector.analyzer.jaeger.proto.query_pb2 import *
from duetector.analyzer.jaeger.proto.query_pb2_grpc import *
from duetector.extension.analyzer import hookimpl


class JaegerAnalyzer(Analyzer):
    default_config = {
        "disabled": True,
    }


@hookimpl
def init_analyzer(config):
    return JaegerAnalyzer(config)


if __name__ == "__main__":

    async def run() -> None:
        async with grpc.aio.insecure_channel("localhost:16685") as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetServices(GetServicesRequest())
            print(response)

    asyncio.run(run())
