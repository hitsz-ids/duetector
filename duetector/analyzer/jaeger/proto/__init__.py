import sys
from os.path import dirname

# Fix invalid proto descriptor for file "model.proto"
import opentelemetry.exporter.jaeger.proto.grpc  # noqa

sys.path.append(dirname(__file__))
