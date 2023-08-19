from .base import Collector

__all__ = ["Collector"]

# Expose init_collector for plugin system
from .base import init_collector  # noqa
