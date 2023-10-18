# Expose for plugin system
from . import base, db, otel

registers = [base, db, otel]
