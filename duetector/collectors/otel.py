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
from duetector.otel import OTelInspector
from duetector.utils import Singleton, get_grpc_cred_from_path


class OTelInitiator(metaclass=Singleton):
    """
    Host the OpenTelemetry SDK and initialize the provider and exporter.

    Avaliable exporters:
        - ``console``
        - ``otlp-grpc``
        - ``otlp-http``
        - ``jaeger-thrift``
        - ``jaeger-grpc``
        - ``zipkin-http``
        - ``zipkin-json``
        - ``prometheus``

    Example:

    .. code-block:: python

            otel = OTelInitiator()
            trace = otel.initialize(
                service_name="duetector",
                exporter="console",
            )

            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("test") as span:
                span.set_attribute("test", "test")

            otel.shutdown()
    """

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
        if self._initialized and self.provider:
            self.provider.shutdown()
            self._initialized = False
            self.provider = None


class OTelCollector(Collector, OTelInspector):
    """
    A collector using OpenTelemetry SDK.

    Config:
        - ``exporter``: One of ``console``, ``otlp-grpc``, ``otlp-http``, ``jaeger-thrift``, ``jaeger-grpc``, ``zipkin-http``, ``zipkin-json``, see :class:`OTelInitiator` for more details
        - ``exporter_kwargs``: A dict of kwargs for exporter

    Note:
        Since v1.35, the Jaeger supports OTLP natively. Please use the OTLP exporter instead. Support for this exporter will end July 2023.

    """

    service_prefix = "duetector"
    service_sep = "-"

    default_config = {
        **Collector.default_config,
        "disabled": True,
        "exporter": "console",
        "exporter_kwargs": {},
        "grpc_exporter_kwargs": {
            "secure": False,
            "root_certificates_path": "",
            "private_key_path": "",
            "certificate_chain_path": "",
        },
    }

    @property
    def exporter(self) -> str:
        return self.config.exporter

    @property
    def endpoint(self) -> Optional[str]:
        return self.config.endpoint

    @property
    def exporter_kwargs(self) -> Dict[str, Any]:
        return self.config.exporter_kwargs._config_dict

    @property
    def service_name(self) -> str:
        return self.generate_service_name(self.id)

    @property
    def grpc_exporter_kwargs(self) -> Dict[str, Any]:
        kwargs = self.config.grpc_exporter_kwargs._config_dict
        wrapped_kwargs = {}
        if kwargs.get("secure"):
            creds = get_grpc_cred_from_path(
                root_certificates_path=kwargs.get("root_certificates_path"),
                private_key_path=kwargs.get("private_key_path"),
                certificate_chain_path=kwargs.get("certificate_chain_path"),
            )
            wrapped_kwargs = {
                "insecure": False,
                "credentials": creds,
            }

        return wrapped_kwargs

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        if "grpc" in self.exporter:
            self.exporter_kwargs.update(self.grpc_exporter_kwargs)

        self.otel = OTelInitiator()
        self.otel.initialize(
            service_name=self.service_name,
            exporter=self.exporter,
            exporter_kwargs=self.exporter_kwargs,
        )

    def _emit(self, t: Tracking):
        tracer = trace.get_tracer(self.id)
        with tracer.start_as_current_span(self.generate_span_name(t)) as span:
            t.set_span(self, span)

    def summary(self) -> Dict:
        return {}

    def shutdown(self):
        super().shutdown()
        self.otel.shutdown()


@hookimpl
def init_collector(config):
    return OTelCollector(config)
