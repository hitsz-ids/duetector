from .base import Filter

__all__ = ["Filter"]


# Expose init_filter for plugin system
from .base import init_filter  # noqa
