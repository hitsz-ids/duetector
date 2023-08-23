from typing import Any, Dict, Optional

from duetector.collectors import Collector
from duetector.collectors.models import Tracking
from duetector.extension.collector import hookimpl


class EchoCollector(Collector):
    default_config = {
        **Collector.default_config,  # inherit default_config
        "disabled": False,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    def _emit(self, t: Tracking):
        print(t)

    def summary(self) -> Dict:
        return {}


@hookimpl
def init_collector(config):
    return EchoCollector(config)
