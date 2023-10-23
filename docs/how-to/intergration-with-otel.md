# Integration with OpenTelemetry

[OpenTelemetry](https://opentelemetry.io/) is a collection of APIs, SDKs, and tools that allow development teams to generate, process, and transmit telemetry data in a unified single format.

`duetector` support integration with OpenTelemetry. Through [otel collector](../../duetector/collectors/otel.py), we can export traces to any backend supported by OpenTelemetry.


## Choose a collector

Before we start, we need to choose a collector, which is responsible for receiving traces from `duetector`.



## Enable Otel Collector

To enable otel collector, we need to set `collector.otelcollector.disabled` to `false` in config file, and set `exporter` and its `exporter_kwargs` to specify the backend. Also, you can use environment variables to set the config.

Here is an example config file:

```toml
[collector.otelcollector]
disabled = false
statis_id = ""
exporter = "console"

[collector.otelcollector.backend_args]
max_workers = 10

[collector.otelcollector.exporter_kwargs]
```
