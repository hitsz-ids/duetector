from pathlib import Path

from duetector.collectors.base import Collector
from duetector.collectors.models import Tracking


class JsonCollector(Collector):
    def __init__(self):
        self.file: Path = Path("duetector.jsonlines")

    def _emit(self, t: Tracking):
        self.file.write_text(t.model_dump_json() + "\n", append=True)
