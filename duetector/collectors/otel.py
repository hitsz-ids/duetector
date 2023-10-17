from typing import Any, Dict, Optional

from duetector.collectors.base import Collector
from duetector.collectors.models import Tracking
from duetector.extension.collector import hookimpl


class OTelCollector(Collector):
    default_config = {
        **Collector.default_config,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel

    def _emit(self, t: Tracking):
        pass

    def summary(self) -> Dict:
        # TODO: implement this, only cache data in debug mode(console exporter)
        return {}


@hookimpl
def init_collector(config):
    return OTelCollector(config)
