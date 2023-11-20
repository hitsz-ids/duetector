import asyncio
import functools
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import grpc
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from duetector.exceptions import AnalysQueryError
from duetector.utils import get_grpc_cred_from_path

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.analyzer.base import Analyzer
from duetector.analyzer.jaeger.proto.model_pb2 import Span
from duetector.analyzer.jaeger.proto.query_pb2 import *
from duetector.analyzer.jaeger.proto.query_pb2_grpc import *
from duetector.analyzer.models import AnalyzerBrief, Tracking
from duetector.extension.analyzer import hookimpl
from duetector.otel import OTelInspector

ChannelInitializer = Callable[[], grpc.aio.Channel]


class JaegerConnector(OTelInspector):
    def __init__(self, channel_initializer: ChannelInitializer):
        self.channel_initializer: ChannelInitializer = channel_initializer

    async def inspect_all_collector_ids(self) -> List[str]:
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetServices(GetServicesRequest())
            return [
                self.get_identifier(service)
                for service in response.services
                if self.get_identifier(service)
            ]

    async def get_operation(self, service: str, span_kind: Optional[str] = None) -> List[str]:
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetOperations(
                GetOperationsRequest(service=service, span_kind=span_kind)
            )
            return [operation.name for operation in response.operations]

    async def inspect_all_tracers(self) -> List[str]:
        return [
            await self.get_tracer_name(operation)
            for operation in await self.get_operation(
                service for service in self.inspect_all_collector_ids()
            )
            if self.get_tracer_name(operation)
        ]

    def _datetime_to_protobuf_timestamp(self, dt: datetime) -> Timestamp:
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts

    async def query_trace(
        self,
        collector_id,
        tracer_name,
        tags: Optional[Dict[str, Any]] = None,
        start_time_min: Optional[datetime] = None,
        start_time_max: Optional[datetime] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None,
        search_depth: int = 20,
    ) -> List[Tracking]:
        service_name = self.generate_service_name(collector_id)
        operation_name = self.generate_span_name(tracer_name)
        if start_time_min:
            start_time_min = self._datetime_to_protobuf_timestamp(start_time_min)
        if start_time_max:
            start_time_max = self._datetime_to_protobuf_timestamp(start_time_max)

        # 1 <= search_depth <= 1500
        if search_depth < 1 or search_depth > 1500:
            raise AnalysQueryError("Jaeger search_depth must be between 1 and 1500.")

        request = FindTracesRequest(
            query=TraceQueryParameters(
                service_name=service_name,
                operation_name=operation_name,
                tags=tags,
                start_time_min=start_time_min,
                start_time_max=start_time_max,
                duration_min=Duration(seconds=duration_min) if duration_min else None,
                duration_max=Duration(seconds=duration_max) if duration_max else None,
                search_depth=search_depth,
            )
        )

        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = stub.FindTraces(request)
            ret = []
            async for chunk in response:
                ret.extend([Tracking.from_jaeger_span(tracer_name, span) for span in chunk.spans])
            return ret


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

    async def query(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start: int = 0,
        limit: int = 20,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        distinct: bool = False,
        order_by_asc: Optional[List[str]] = None,
        order_by_desc: Optional[List[str]] = None,
    ) -> List[Tracking]:
        """
        Query all tracking records from jaeger connector.

        Args:
            tracers (Optional[List[str]], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_ids (Optional[List[str]], optional): Collector id. Defaults to None, all collector id will be queried.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            start (int, optional): Not support.
            limit (int, optional): Limit for each tracer of each collector id. Defaults to 20.
            columns (Optional[List[str]], optional): Not support, all tags will be returned.
            where (Optional[Dict[str, Any]], optional): Tags filter. Defaults to None.
            distinct (bool, optional): Not support.
            order_by_asc (Optional[List[str]], optional): Not support.
            order_by_desc (Optional[List[str]], optional): Not support.
        Returns:
            List[duetector.analyzer.models.Tracking]: List of tracking records.
        """
        return [
            await self.connector.query_trace(
                collector_id=collector_id,
                tracer_name=tracer,
                tags=where,
                start_time_min=start_datetime,
                start_time_max=end_datetime,
                search_depth=limit,
            )
            for tracer in tracers
            for collector_id in collector_ids
        ]

    async def brief(
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

    async def analyze(self):
        # TODO: Not design yet.
        pass


@hookimpl
def init_analyzer(config):
    return JaegerAnalyzer(config)


if __name__ == "__main__":

    async def run() -> None:
        Analyzer = JaegerAnalyzer()
        await Analyzer.connector.query_trace(
            collector_id="demo-service", tracer_name="tcp_v4_connect"
        )

    asyncio.run(run())
