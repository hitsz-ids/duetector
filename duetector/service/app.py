from fastapi import Depends, FastAPI

from duetector.__init__ import __version__
from duetector.service.config import get_config
from duetector.service.control.routes import r as cr
from duetector.service.query.routes import r as qr

app = FastAPI(
    title="Duetector",
    description="Data Usage Extensible Detector for data usage observability",
    version=__version__,
)
app.include_router(qr)
app.include_router(cr)
