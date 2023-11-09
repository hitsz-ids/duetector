from opentelemetry.proto.trace.v1 import trace_pb2 as _trace_pb2
from gogoproto import gogo_pb2 as _gogo_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class FindTracesRequest(_message.Message):
    __slots__ = ["query"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: TraceQueryParameters
    def __init__(self, query: _Optional[_Union[TraceQueryParameters, _Mapping]] = ...) -> None: ...

class GetOperationsRequest(_message.Message):
    __slots__ = ["service", "span_kind"]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    SPAN_KIND_FIELD_NUMBER: _ClassVar[int]
    service: str
    span_kind: str
    def __init__(self, service: _Optional[str] = ..., span_kind: _Optional[str] = ...) -> None: ...

class GetOperationsResponse(_message.Message):
    __slots__ = ["operations"]
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    operations: _containers.RepeatedCompositeFieldContainer[Operation]
    def __init__(
        self, operations: _Optional[_Iterable[_Union[Operation, _Mapping]]] = ...
    ) -> None: ...

class GetServicesRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetServicesResponse(_message.Message):
    __slots__ = ["services"]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    services: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, services: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTraceRequest(_message.Message):
    __slots__ = ["end_time", "start_time", "trace_id"]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    end_time: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    trace_id: str
    def __init__(
        self,
        trace_id: _Optional[str] = ...,
        start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class Operation(_message.Message):
    __slots__ = ["name", "span_kind"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SPAN_KIND_FIELD_NUMBER: _ClassVar[int]
    name: str
    span_kind: str
    def __init__(self, name: _Optional[str] = ..., span_kind: _Optional[str] = ...) -> None: ...

class SpansResponseChunk(_message.Message):
    __slots__ = ["resource_spans"]
    RESOURCE_SPANS_FIELD_NUMBER: _ClassVar[int]
    resource_spans: _containers.RepeatedCompositeFieldContainer[_trace_pb2.ResourceSpans]
    def __init__(
        self, resource_spans: _Optional[_Iterable[_Union[_trace_pb2.ResourceSpans, _Mapping]]] = ...
    ) -> None: ...

class TraceQueryParameters(_message.Message):
    __slots__ = [
        "attributes",
        "duration_max",
        "duration_min",
        "num_traces",
        "operation_name",
        "service_name",
        "start_time_max",
        "start_time_min",
    ]

    class AttributesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DURATION_MAX_FIELD_NUMBER: _ClassVar[int]
    DURATION_MIN_FIELD_NUMBER: _ClassVar[int]
    NUM_TRACES_FIELD_NUMBER: _ClassVar[int]
    OPERATION_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_MAX_FIELD_NUMBER: _ClassVar[int]
    START_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    attributes: _containers.ScalarMap[str, str]
    duration_max: _duration_pb2.Duration
    duration_min: _duration_pb2.Duration
    num_traces: int
    operation_name: str
    service_name: str
    start_time_max: _timestamp_pb2.Timestamp
    start_time_min: _timestamp_pb2.Timestamp
    def __init__(
        self,
        service_name: _Optional[str] = ...,
        operation_name: _Optional[str] = ...,
        attributes: _Optional[_Mapping[str, str]] = ...,
        start_time_min: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        start_time_max: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        duration_min: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        duration_max: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        num_traces: _Optional[int] = ...,
    ) -> None: ...
