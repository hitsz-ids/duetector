from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

BINARY: ValueType
BOOL: ValueType
CHILD_OF: SpanRefType
DESCRIPTOR: _descriptor.FileDescriptor
FLOAT64: ValueType
FOLLOWS_FROM: SpanRefType
INT64: ValueType
STRING: ValueType

class Batch(_message.Message):
    __slots__ = ["process", "spans"]
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    SPANS_FIELD_NUMBER: _ClassVar[int]
    process: Process
    spans: _containers.RepeatedCompositeFieldContainer[Span]
    def __init__(
        self,
        spans: _Optional[_Iterable[_Union[Span, _Mapping]]] = ...,
        process: _Optional[_Union[Process, _Mapping]] = ...,
    ) -> None: ...

class DependencyLink(_message.Message):
    __slots__ = ["call_count", "child", "parent", "source"]
    CALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    CHILD_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    call_count: int
    child: str
    parent: str
    source: str
    def __init__(
        self,
        parent: _Optional[str] = ...,
        child: _Optional[str] = ...,
        call_count: _Optional[int] = ...,
        source: _Optional[str] = ...,
    ) -> None: ...

class KeyValue(_message.Message):
    __slots__ = ["key", "v_binary", "v_bool", "v_float64", "v_int64", "v_str", "v_type"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    V_BINARY_FIELD_NUMBER: _ClassVar[int]
    V_BOOL_FIELD_NUMBER: _ClassVar[int]
    V_FLOAT64_FIELD_NUMBER: _ClassVar[int]
    V_INT64_FIELD_NUMBER: _ClassVar[int]
    V_STR_FIELD_NUMBER: _ClassVar[int]
    V_TYPE_FIELD_NUMBER: _ClassVar[int]
    key: str
    v_binary: bytes
    v_bool: bool
    v_float64: float
    v_int64: int
    v_str: str
    v_type: ValueType
    def __init__(
        self,
        key: _Optional[str] = ...,
        v_type: _Optional[_Union[ValueType, str]] = ...,
        v_str: _Optional[str] = ...,
        v_bool: bool = ...,
        v_int64: _Optional[int] = ...,
        v_float64: _Optional[float] = ...,
        v_binary: _Optional[bytes] = ...,
    ) -> None: ...

class Log(_message.Message):
    __slots__ = ["fields", "timestamp"]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedCompositeFieldContainer[KeyValue]
    timestamp: _timestamp_pb2.Timestamp
    def __init__(
        self,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        fields: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ...,
    ) -> None: ...

class Process(_message.Message):
    __slots__ = ["service_name", "tags"]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    tags: _containers.RepeatedCompositeFieldContainer[KeyValue]
    def __init__(
        self,
        service_name: _Optional[str] = ...,
        tags: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ...,
    ) -> None: ...

class Span(_message.Message):
    __slots__ = [
        "duration",
        "flags",
        "logs",
        "operation_name",
        "process",
        "process_id",
        "references",
        "span_id",
        "start_time",
        "tags",
        "trace_id",
        "warnings",
    ]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    OPERATION_NAME_FIELD_NUMBER: _ClassVar[int]
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    duration: _duration_pb2.Duration
    flags: int
    logs: _containers.RepeatedCompositeFieldContainer[Log]
    operation_name: str
    process: Process
    process_id: str
    references: _containers.RepeatedCompositeFieldContainer[SpanRef]
    span_id: bytes
    start_time: _timestamp_pb2.Timestamp
    tags: _containers.RepeatedCompositeFieldContainer[KeyValue]
    trace_id: bytes
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        trace_id: _Optional[bytes] = ...,
        span_id: _Optional[bytes] = ...,
        operation_name: _Optional[str] = ...,
        references: _Optional[_Iterable[_Union[SpanRef, _Mapping]]] = ...,
        flags: _Optional[int] = ...,
        start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        tags: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ...,
        logs: _Optional[_Iterable[_Union[Log, _Mapping]]] = ...,
        process: _Optional[_Union[Process, _Mapping]] = ...,
        process_id: _Optional[str] = ...,
        warnings: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class SpanRef(_message.Message):
    __slots__ = ["ref_type", "span_id", "trace_id"]
    REF_TYPE_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    ref_type: SpanRefType
    span_id: bytes
    trace_id: bytes
    def __init__(
        self,
        trace_id: _Optional[bytes] = ...,
        span_id: _Optional[bytes] = ...,
        ref_type: _Optional[_Union[SpanRefType, str]] = ...,
    ) -> None: ...

class Trace(_message.Message):
    __slots__ = ["process_map", "spans", "warnings"]

    class ProcessMapping(_message.Message):
        __slots__ = ["process", "process_id"]
        PROCESS_FIELD_NUMBER: _ClassVar[int]
        PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
        process: Process
        process_id: str
        def __init__(
            self,
            process_id: _Optional[str] = ...,
            process: _Optional[_Union[Process, _Mapping]] = ...,
        ) -> None: ...
    PROCESS_MAP_FIELD_NUMBER: _ClassVar[int]
    SPANS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    process_map: _containers.RepeatedCompositeFieldContainer[Trace.ProcessMapping]
    spans: _containers.RepeatedCompositeFieldContainer[Span]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        spans: _Optional[_Iterable[_Union[Span, _Mapping]]] = ...,
        process_map: _Optional[_Iterable[_Union[Trace.ProcessMapping, _Mapping]]] = ...,
        warnings: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SpanRefType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
