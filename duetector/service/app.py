from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query

from duetector.__init__ import __version__
from duetector.service.config import Config, get_server_config
from duetector.service.control.routes import r as cr
from duetector.service.query.routes import r as qr


async def verify_token(
    server_config: Config = Depends(get_server_config),
    token: Optional[str] = Query(default=""),
):
    if server_config.token and token != server_config.token:
        raise HTTPException(403, "Invalid token")


app = FastAPI(
    title="Duetector",
    description="Data Usage Extensible Detector for data usage observability",
    version=__version__,
    dependencies=[Depends(verify_token)],
)
app.include_router(qr)
app.include_router(cr)
