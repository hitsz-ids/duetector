# Fix invalid proto descriptor for file "model.proto"
import sys
from os.path import dirname

import opentelemetry.exporter.jaeger.proto.grpc  # noqa

sys.path.append(dirname(__file__))
