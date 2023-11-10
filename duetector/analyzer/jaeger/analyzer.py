import asyncio

import grpc

from duetector.analyzer.jaeger.proto.query_pb2 import *
from duetector.analyzer.jaeger.proto.query_pb2_grpc import *


async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:16685") as channel:
        stub = QueryServiceStub(channel)
        response = await stub.GetServices(GetServicesRequest())
        print(response)


if __name__ == "__main__":
    asyncio.run(run())
