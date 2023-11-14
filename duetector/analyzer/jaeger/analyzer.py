import asyncio
import functools
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import grpc

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.analyzer.base import Analyzer
from duetector.analyzer.jaeger.proto.query_pb2 import *
from duetector.analyzer.jaeger.proto.query_pb2_grpc import *
from duetector.analyzer.models import AnalyzerBrief, Tracking
from duetector.collectors.otel import OTelCollector
from duetector.extension.analyzer import hookimpl

ChannelInitializer = Callable[[], grpc.aio.Channel]


class JaegerConnector:
    def __init__(self, channel_initializer: ChannelInitializer):
        self.channel_initializer: ChannelInitializer = channel_initializer

    def inspect_all_service(self):
        pass

    def inspect_all_operation(self):
        pass


class JaegerAnalyzer(Analyzer):
    default_config = {
        "disabled": True,
        # TODO: Support secure channel
        # "secure_channel": False,
        "host": "localhost",
        "port": 16685,
    }
    service_prefix = OTelCollector.service_prefix
    service_sep = OTelCollector.service_sep

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    @property
    @cache
    def channel(self) -> ChannelInitializer:
        """
        Example:
            async with self.channel as channel:
                stub = QueryServiceStub(channel)
                response = await stub.GetServices(GetServicesRequest())
                print(response)

        """
        target_func = grpc.aio.insecure_channel
        kwargs = {"target": f"{self.config.host}:{self.config.port}"}

        return functools.partial(target_func, **kwargs)

    @property
    @cache
    def connector(self):
        return JaegerConnector(self.channel)

    def get_all_tracers(self) -> List[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """

        raise NotImplementedError

    def get_all_collector_ids(self) -> List[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        raise NotImplementedError

    def query(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start: int = 0,
        limit: int = 0,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        distinct: bool = False,
        order_by_asc: Optional[List[str]] = None,
        order_by_desc: Optional[List[str]] = None,
    ) -> List[Tracking]:
        """
        Query all tracking records from database.

        Args:
            tracers (Optional[List[str]], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_ids (Optional[List[str]], optional): Collector id. Defaults to None, all collector id will be queried.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            start (int, optional): Start index. Defaults to 0.
            limit (int, optional): Limit of records. Defaults to 20. ``0`` means no limit.
            columns (Optional[List[str]], optional): Columns to query. Defaults to None, all columns will be queried.
            where (Optional[Dict[str, Any]], optional): Where clause. Defaults to None.
            distinct (bool, optional): Distinct. Defaults to False.
            order_by_asc (Optional[List[str]], optional): Order by asc. Defaults to None.
            order_by_desc (Optional[List[str]], optional): Order by desc. Defaults to None.
        Returns:
            List[duetector.analyzer.models.Tracking]: List of tracking records.
        """
        raise NotImplementedError

    def brief(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        with_details: bool = True,
        distinct: bool = False,
        inspect_type: bool = False,
    ) -> AnalyzerBrief:
        """
        Get a brief of this analyzer.

        Args:
            tracers (Optional[List[str]], optional):
                Tracers. Defaults to None, all tracers will be queried.
                If a specific tracer is not found, it will be ignored.
            collector_ids (Optional[List[str]], optional):
                Collector ids. Defaults to None, all collector ids will be queried.
                If a specific collector id is not found, it will be ignored.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            with_details (bool, optional): With details. Defaults to True.
            distinct (bool, optional): Distinct. Defaults to False.
            inspect_type (bool, optional): Weather fileds's value is type or type name. Defaults to False, type name.

        Returns:
            AnalyzerBrief: A brief of this analyzer.
        """
        raise NotImplementedError

    def analyze(self):
        # TODO: Not design yet.
        pass


@hookimpl
def init_analyzer(config):
    return JaegerAnalyzer(config)


if __name__ == "__main__":

    async def run() -> None:
        async with JaegerAnalyzer().channel() as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetServices(GetServicesRequest())
            print(response)

    asyncio.run(run())