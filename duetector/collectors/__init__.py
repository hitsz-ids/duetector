# Expose init_collector for plugin system
# Expose for plugin system
from . import base, sqlite
from .base import Collector

registers = [base, sqlite]
