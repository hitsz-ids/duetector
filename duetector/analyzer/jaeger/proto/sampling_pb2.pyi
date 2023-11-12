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

DESCRIPTOR: _descriptor.FileDescriptor
PROBABILISTIC: SamplingStrategyType
RATE_LIMITING: SamplingStrategyType

class OperationSamplingStrategy(_message.Message):
    __slots__ = ["operation", "probabilisticSampling"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    PROBABILISTICSAMPLING_FIELD_NUMBER: _ClassVar[int]
    operation: str
    probabilisticSampling: ProbabilisticSamplingStrategy
    def __init__(
        self,
        operation: _Optional[str] = ...,
        probabilisticSampling: _Optional[_Union[ProbabilisticSamplingStrategy, _Mapping]] = ...,
    ) -> None: ...

class PerOperationSamplingStrategies(_message.Message):
    __slots__ = [
        "defaultLowerBoundTracesPerSecond",
        "defaultSamplingProbability",
        "defaultUpperBoundTracesPerSecond",
        "perOperationStrategies",
    ]
    DEFAULTLOWERBOUNDTRACESPERSECOND_FIELD_NUMBER: _ClassVar[int]
    DEFAULTSAMPLINGPROBABILITY_FIELD_NUMBER: _ClassVar[int]
    DEFAULTUPPERBOUNDTRACESPERSECOND_FIELD_NUMBER: _ClassVar[int]
    PEROPERATIONSTRATEGIES_FIELD_NUMBER: _ClassVar[int]
    defaultLowerBoundTracesPerSecond: float
    defaultSamplingProbability: float
    defaultUpperBoundTracesPerSecond: float
    perOperationStrategies: _containers.RepeatedCompositeFieldContainer[OperationSamplingStrategy]
    def __init__(
        self,
        defaultSamplingProbability: _Optional[float] = ...,
        defaultLowerBoundTracesPerSecond: _Optional[float] = ...,
        perOperationStrategies: _Optional[
            _Iterable[_Union[OperationSamplingStrategy, _Mapping]]
        ] = ...,
        defaultUpperBoundTracesPerSecond: _Optional[float] = ...,
    ) -> None: ...

class ProbabilisticSamplingStrategy(_message.Message):
    __slots__ = ["samplingRate"]
    SAMPLINGRATE_FIELD_NUMBER: _ClassVar[int]
    samplingRate: float
    def __init__(self, samplingRate: _Optional[float] = ...) -> None: ...

class RateLimitingSamplingStrategy(_message.Message):
    __slots__ = ["maxTracesPerSecond"]
    MAXTRACESPERSECOND_FIELD_NUMBER: _ClassVar[int]
    maxTracesPerSecond: int
    def __init__(self, maxTracesPerSecond: _Optional[int] = ...) -> None: ...

class SamplingStrategyParameters(_message.Message):
    __slots__ = ["serviceName"]
    SERVICENAME_FIELD_NUMBER: _ClassVar[int]
    serviceName: str
    def __init__(self, serviceName: _Optional[str] = ...) -> None: ...

class SamplingStrategyResponse(_message.Message):
    __slots__ = [
        "operationSampling",
        "probabilisticSampling",
        "rateLimitingSampling",
        "strategyType",
    ]
    OPERATIONSAMPLING_FIELD_NUMBER: _ClassVar[int]
    PROBABILISTICSAMPLING_FIELD_NUMBER: _ClassVar[int]
    RATELIMITINGSAMPLING_FIELD_NUMBER: _ClassVar[int]
    STRATEGYTYPE_FIELD_NUMBER: _ClassVar[int]
    operationSampling: PerOperationSamplingStrategies
    probabilisticSampling: ProbabilisticSamplingStrategy
    rateLimitingSampling: RateLimitingSamplingStrategy
    strategyType: SamplingStrategyType
    def __init__(
        self,
        strategyType: _Optional[_Union[SamplingStrategyType, str]] = ...,
        probabilisticSampling: _Optional[_Union[ProbabilisticSamplingStrategy, _Mapping]] = ...,
        rateLimitingSampling: _Optional[_Union[RateLimitingSamplingStrategy, _Mapping]] = ...,
        operationSampling: _Optional[_Union[PerOperationSamplingStrategies, _Mapping]] = ...,
    ) -> None: ...

class SamplingStrategyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
