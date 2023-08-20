from .base import Filter

__all__ = ["Filter"]


# Expose for plugin system
from . import base

registers = [base]
