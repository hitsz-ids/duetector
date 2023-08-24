from .base import Collector

__all__ = ["Collector"]


# Expose for plugin system
from . import base, db

registers = [base, db]
