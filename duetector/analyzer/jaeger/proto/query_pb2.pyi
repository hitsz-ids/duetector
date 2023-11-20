import model_pb2 as _model_pb2
from google.api import annotations_pb2 as _annotations_pb2
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

class ArchiveTraceRequest(_message.Message):
    __slots__ = ["end_time", "start_time", "trace_id"]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    end_time: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    trace_id: bytes
    def __init__(
        self,
        trace_id: _Optional[bytes] = ...,
        start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class ArchiveTraceResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class FindTracesRequest(_message.Message):
    __slots__ = ["query"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: TraceQueryParameters
    def __init__(self, query: _Optional[_Union[TraceQueryParameters, _Mapping]] = ...) -> None: ...

class GetDependenciesRequest(_message.Message):
    __slots__ = ["end_time", "start_time"]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    end_time: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    def __init__(
        self,
        start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class GetDependenciesResponse(_message.Message):
    __slots__ = ["dependencies"]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    dependencies: _containers.RepeatedCompositeFieldContainer[_model_pb2.DependencyLink]
    def __init__(
        self,
        dependencies: _Optional[_Iterable[_Union[_model_pb2.DependencyLink, _Mapping]]] = ...,
    ) -> None: ...

class GetOperationsRequest(_message.Message):
    __slots__ = ["service", "span_kind"]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    SPAN_KIND_FIELD_NUMBER: _ClassVar[int]
    service: str
    span_kind: str
    def __init__(self, service: _Optional[str] = ..., span_kind: _Optional[str] = ...) -> None: ...

class GetOperationsResponse(_message.Message):
    __slots__ = ["operationNames", "operations"]
    OPERATIONNAMES_FIELD_NUMBER: _ClassVar[int]
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    operationNames: _containers.RepeatedScalarFieldContainer[str]
    operations: _containers.RepeatedCompositeFieldContainer[Operation]
    def __init__(
        self,
        operationNames: _Optional[_Iterable[str]] = ...,
        operations: _Optional[_Iterable[_Union[Operation, _Mapping]]] = ...,
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
    trace_id: bytes
    def __init__(
        self,
        trace_id: _Optional[bytes] = ...,
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
    __slots__ = ["spans"]
    SPANS_FIELD_NUMBER: _ClassVar[int]
    spans: _containers.RepeatedCompositeFieldContainer[_model_pb2.Span]
    def __init__(
        self, spans: _Optional[_Iterable[_Union[_model_pb2.Span, _Mapping]]] = ...
    ) -> None: ...

class TraceQueryParameters(_message.Message):
    __slots__ = [
        "duration_max",
        "duration_min",
        "operation_name",
        "search_depth",
        "service_name",
        "start_time_max",
        "start_time_min",
        "tags",
    ]

    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DURATION_MAX_FIELD_NUMBER: _ClassVar[int]
    DURATION_MIN_FIELD_NUMBER: _ClassVar[int]
    OPERATION_NAME_FIELD_NUMBER: _ClassVar[int]
    SEARCH_DEPTH_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_MAX_FIELD_NUMBER: _ClassVar[int]
    START_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    duration_max: _duration_pb2.Duration
    duration_min: _duration_pb2.Duration
    operation_name: str
    search_depth: int
    service_name: str
    start_time_max: _timestamp_pb2.Timestamp
    start_time_min: _timestamp_pb2.Timestamp
    tags: _containers.ScalarMap[str, str]
    def __init__(
        self,
        service_name: _Optional[str] = ...,
        operation_name: _Optional[str] = ...,
        tags: _Optional[_Mapping[str, str]] = ...,
        start_time_min: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        start_time_max: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        duration_min: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        duration_max: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        search_depth: _Optional[int] = ...,
    ) -> None: ...
