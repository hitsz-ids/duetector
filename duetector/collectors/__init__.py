# Expose init_collector for plugin system
# Expose for plugin system
from . import base, db
from .base import Collector

registers = [base, db]
