import model_pb2 as _model_pb2
from gogoproto import gogo_pb2 as _gogo_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class PostSpansRequest(_message.Message):
    __slots__ = ["batch"]
    BATCH_FIELD_NUMBER: _ClassVar[int]
    batch: _model_pb2.Batch
    def __init__(self, batch: _Optional[_Union[_model_pb2.Batch, _Mapping]] = ...) -> None: ...

class PostSpansResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
