from __future__ import annotations

import asyncio
import functools
from datetime import datetime
from typing import Any, Callable

import grpc
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from duetector.analyzer.jaeger.proto import model_pb2
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
from duetector.analyzer.models import AnalyzerBrief, Brief, Tracking
from duetector.extension.analyzer import hookimpl
from duetector.log import logger
from duetector.otel import OTelInspector

ChannelInitializer = Callable[[], grpc.aio.Channel]


class JaegerConnector(OTelInspector):
    """
    Providing query method for jaeger backend
    """

    def __init__(self, channel_initializer: ChannelInitializer):
        self.channel_initializer: ChannelInitializer = channel_initializer

    async def inspect_all_collector_ids(self) -> list[str]:
        logger.info("Querying all collector ids...")
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetServices(GetServicesRequest())
            return [
                self.get_identifier(service)
                for service in response.services
                if self.get_identifier(service)
            ]

    async def get_operation(self, service: str, span_kind: str | None = None) -> list[str]:
        logger.info(f"Querying operations of {service}...")
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = await stub.GetOperations(
                GetOperationsRequest(service=service, span_kind=span_kind)
            )
            return [operation.name for operation in response.operations]

    async def inspect_all_tracers(self) -> list[str]:
        logger.info("Querying all tracers...")
        ret = []
        for collector_id in await self.inspect_all_collector_ids():
            service = self.generate_service_name(collector_id)
            for operation in await self.get_operation(service):
                tracer_name = self.get_tracer_name(operation)
                if tracer_name and tracer_name not in ret:
                    ret.append(tracer_name)
        return ret

    def _datetime_to_protobuf_timestamp(self, dt: datetime) -> Timestamp:
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts

    def _protobuf_timestamp_to_datetime(self, ts: Timestamp) -> datetime:
        return ts.ToDatetime()

    def get_find_tracers_request(
        self,
        collector_id: str,
        tracer_name: str,
        tags: dict[str, Any] | None = None,
        start_time_min: datetime | None = None,
        start_time_max: datetime | None = None,
        duration_min: int | None = None,
        duration_max: int | None = None,
        search_depth: int = 20,
    ) -> FindTracesRequest:
        if not collector_id:
            raise AnalysQueryError(f"collector_id is required, current:{collector_id}")
        if not tracer_name:
            raise AnalysQueryError(f"tracer_name is required, current:{tracer_name}")
        if search_depth < 1 or search_depth > 1500:
            raise AnalysQueryError("Jaeger search_depth must be between 1 and 1500.")

        return FindTracesRequest(
            query=TraceQueryParameters(
                service_name=self.generate_service_name(collector_id),
                operation_name=self.generate_span_name(tracer_name),
                tags=tags,
                start_time_min=self._datetime_to_protobuf_timestamp(start_time_min)
                if start_time_min
                else None,
                start_time_max=self._datetime_to_protobuf_timestamp(start_time_max)
                if start_time_max
                else None,
                duration_min=Duration(seconds=duration_min) if duration_min else None,
                duration_max=Duration(seconds=duration_max) if duration_max else None,
                search_depth=search_depth,
            )
        )

    async def query_trace(
        self,
        collector_id: str,
        tracer_name: str,
        tags: dict[str, Any] = None,
        start_time_min: datetime | None = None,
        start_time_max: datetime | None = None,
        duration_min: int | None = None,
        duration_max: int | None = None,
        search_depth: int = 20,
    ) -> list[Tracking]:
        if not collector_id:
            raise AnalysQueryError(f"collector_id is required, current:{collector_id}")
        if not tracer_name:
            raise AnalysQueryError(f"tracer_name is required, current:{tracer_name}")
        request = self.get_find_tracers_request(
            collector_id=collector_id,
            tracer_name=tracer_name,
            tags=tags,
            start_time_min=start_time_min,
            start_time_max=start_time_max,
            duration_min=duration_min,
            duration_max=duration_max,
            search_depth=search_depth,
        )
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = stub.FindTraces(request)
            ret = []
            async for chunk in response:
                ret.extend([Tracking.from_jaeger_span(tracer_name, span) for span in chunk.spans])
            return ret

    def inspect_span(self, span: Span) -> dict[str, Any]:
        value_type_to_field_attr = {
            model_pb2.STRING: "str",
            model_pb2.BOOL: "bool",
            model_pb2.INT64: "int",
            model_pb2.FLOAT64: "float",
            model_pb2.BINARY: "bytes",
        }

        return {msg.key: value_type_to_field_attr[msg.v_type] for msg in span.tags}

    async def brief(
        self,
        collector_id: str,
        tracer_name: str,
        start_time_min: datetime | None = None,
        start_time_max: datetime | None = None,
        inspect_type=True,
    ) -> Brief | None:
        if not collector_id:
            raise AnalysQueryError(f"collector_id is required, current:{collector_id}")
        if not tracer_name:
            raise AnalysQueryError(f"tracer_name is required, current:{tracer_name}")
        request = self.get_find_tracers_request(
            collector_id=collector_id,
            tracer_name=tracer_name,
            start_time_min=start_time_min,
            start_time_max=start_time_max,
            search_depth=1500,
        )
        start_span = last_span = None
        count = 0
        async with self.channel_initializer() as channel:
            stub = QueryServiceStub(channel)
            response = stub.FindTraces(request)
            async for chunk in response:
                if not chunk.spans:
                    break
                spans = [span for span in chunk.spans]
                count += len(spans)
                start_span = spans[0]
                last_span = spans[-1]

        if not (start_span and last_span):
            return None

        return Brief(
            tracer=tracer_name,
            collector_id=collector_id,
            start=self._protobuf_timestamp_to_datetime(start_span.start_time),
            end=self._protobuf_timestamp_to_datetime(last_span.start_time),
            fields={msg.key: None for msg in start_span.tags}
            if not inspect_type
            else self.inspect_span(start_span),
            count=count,
        )


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

    def __init__(self, config: dict[str, Any] | None = None, *args, **kwargs):
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

    async def get_all_tracers(self) -> list[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """

        return await self.connector.inspect_all_tracers()

    async def get_all_collector_ids(self) -> list[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        return await self.connector.inspect_all_collector_ids()

    async def query(
        self,
        tracers: list[str] | None = None,
        collector_ids: list[str] | None = None,
        start_datetime: datetime | None = None,
        end_datetime: list[datetime] | None = None,
        start: int = 0,
        limit: int = 20,
        columns: list[str] | None = None,
        where: dict[str, Any] | None = None,
        distinct: bool = False,
        order_by_asc: list[str] | None = None,
        order_by_desc: list[str] | None = None,
    ) -> list[Tracking]:
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
        not_support_params = {
            "start": start,
            "columns": columns,
            "distinct": distinct,
            "order_by_asc": order_by_asc,
            "order_by_desc": order_by_desc,
        }
        for k, v in not_support_params.items():
            if v:
                logger.warning("Not support params: %s=%s", k, v)

        if not collector_ids:
            collector_ids = await self.get_all_collector_ids()
        if not tracers:
            tracers = await self.get_all_tracers()

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
        tracers: list[str] | None = None,
        collector_ids: list[str] | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        with_details: bool = False,
        distinct: bool = False,
        inspect_type: bool = True,
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
        not_support_params = {
            "with_details": with_details,
            "distinct": distinct,
        }
        for k, v in not_support_params.items():
            if v:
                logger.warning("Not support params: %s=%s", k, v)

        if tracers:
            tracers = [t for t in tracers if t in await self.get_all_tracers()]
        else:
            tracers = await self.get_all_tracers()
        if collector_ids:
            collector_ids = [c for c in collector_ids if c in await self.get_all_collector_ids()]
        else:
            collector_ids = await self.get_all_collector_ids()

        briefs: list[Brief | None] = [
            await self.connector.brief(
                collector_id=collector_id,
                tracer_name=tracer,
                start_time_min=start_datetime,
                start_time_max=end_datetime,
                inspect_type=inspect_type,
            )
            for tracer in tracers
            for collector_id in collector_ids
        ]

        return AnalyzerBrief(
            tracers=set(tracers),
            collector_ids=set(collector_ids),
            briefs={f"{brief.tracer}@{brief.collector_id}": brief for brief in briefs if brief},
        )

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
