import asyncio
import functools
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import grpc

from duetector.utils import get_grpc_cred_from_path

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.analyzer.base import Analyzer
from duetector.analyzer.jaeger.proto.query_pb2 import *
from duetector.analyzer.jaeger.proto.query_pb2_grpc import *
from duetector.analyzer.models import AnalyzerBrief, Tracking
from duetector.collectors.otel import OTelInspector
from duetector.extension.analyzer import hookimpl

ChannelInitializer = Callable[[], grpc.aio.Channel]


class JaegerConnector(OTelInspector):
    def __init__(self, channel_initializer: ChannelInitializer):
        self.channel_initializer: ChannelInitializer = channel_initializer

    def inspect_all_collector_ids(self) -> List[str]:
        with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = stub.GetServices(GetServicesRequest())
            return [
                self.get_identifier(service)
                for service in response.services
                if self.get_identifier(service)
            ]

    def get_operation(self, service: str, span_kind: Optional[str] = None) -> List[str]:
        with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = stub.GetOperations(
                GetOperationsRequest(service=service, span_kind=span_kind)
            )
            return [operation.name for operation in response.operations]

    def inspect_all_tracers(self) -> List[str]:
        return [
            self.get_tracer_name(operation)
            for operation in self.get_operation(
                service for service in self.inspect_all_collector_ids()
            )
            if self.get_tracer_name(operation)
        ]


class JaegerAnalyzer(Analyzer):
    default_config = {
        "disabled": True,
        "secure": False,
        "root_certificates_path": "",
        "private_key_path": "",
        "certificate_chain_path": "",
        "host": "localhost",
        "port": 16685,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    @property
    @cache
    def channel_initializer(self) -> ChannelInitializer:
        """
        Example:
            async with self.channel as channel:
                stub = QueryServiceStub(channel)
                response = await stub.GetServices(GetServicesRequest())
                print(response)

        """
        kwargs = {}
        if self.config.secure:
            target_func = grpc.aio.secure_channel
            kwargs["credentials"] = get_grpc_cred_from_path(
                root_certificates_path=self.config.root_certificates_path,
                private_key_path=self.config.private_key_path,
                certificate_chain_path=self.config.certificate_chain_path,
            )
        else:
            target_func = grpc.aio.insecure_channel
        kwargs["target"] = f"{self.config.host}:{self.config.port}"

        return functools.partial(target_func, **kwargs)

    @property
    @cache
    def connector(self):
        return JaegerConnector(self.channel_initializer)

    def get_all_tracers(self) -> List[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """

        return self.connector.inspect_all_tracers()

    def get_all_collector_ids(self) -> List[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        return self.connector.inspect_all_collector_ids()

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
