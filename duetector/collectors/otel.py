from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.proto.grpc import (
    JaegerExporter as GRPCJaegerExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter as ThriftJaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GRPCOTLPSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPOTLPSpanExporter,
)
from opentelemetry.exporter.zipkin.json import ZipkinExporter as JSONZipkinExporter
from opentelemetry.exporter.zipkin.proto.http import (
    ZipkinExporter as HTTPZipkinExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from duetector.collectors.base import Collector
from duetector.collectors.models import Tracking
from duetector.extension.collector import hookimpl


class OTelInitiator:
    exporter_cls = {
        "console": ConsoleSpanExporter,
        "otlp-grpc": GRPCOTLPSpanExporter,
        "otlp-http": HTTPOTLPSpanExporter,
        "jaeger-thrift": ThriftJaegerExporter,
        "jaeger-grpc": GRPCJaegerExporter,
        "zipkin-http": HTTPZipkinExporter,
        "zipkin-json": JSONZipkinExporter,
        # Prometheus only support metrics
        # "prometheus": "TODO"
    }

    def __init__(self):
        self._initialized = False
        self.provider = None

    def initialize(
        self,
        service_name="unknown-service",
        resource_kwargs: Optional[Dict[str, Any]] = None,
        provider_kwargs: Optional[Dict[str, Any]] = None,
        exporter="console",
        exporter_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self._initialized:
            return

        if not resource_kwargs:
            resource_kwargs = {}
        resource_kwargs.setdefault(SERVICE_NAME, service_name)
        resource = Resource(attributes=resource_kwargs)

        if not provider_kwargs:
            provider_kwargs = {}
        provider = TracerProvider(resource=resource, **provider_kwargs)
        self.provider = provider

        if not exporter_kwargs:
            exporter_kwargs = {}
        processor = BatchSpanProcessor(self.exporter_cls[exporter](**exporter_kwargs))

        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self._initialized = True

    def shutdown(self):
        self.provider.shutdown()
        self.provider = None


class OTelCollector(Collector):
    default_config = {
        **Collector.default_config,
        "disabled": True,
        "mode": "console",
        "exporter_kwargs": {},
    }

    @property
    def mode(self) -> str:
        return self.config.mode

    @property
    def endpoint(self) -> Optional[str]:
        return self.config.endpoint

    @property
    def exporter_kwargs(self) -> Dict[str, Any]:
        return self.config.exporter_kwargs

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.otel = OTelInitiator()
        self.otel.initialize(
            service_name="duetector",
            exporter=self.mode,
            exporter_kwargs=self.exporter_kwargs,
        )

    def _emit(self, t: Tracking):
        tracer = trace.get_tracer(self.id)
        with tracer.start_as_current_span(t.tracer) as span:
            t.set_span(span)

    def summary(self) -> Dict:
        return {}

    def shutdown(self):
        super().shutdown()
        self.otel.shutdown()


@hookimpl
def init_collector(config):
    return OTelCollector(config)
