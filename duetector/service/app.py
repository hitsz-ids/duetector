from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN

from duetector.__init__ import __version__
from duetector.service.config import Config, get_server_config
from duetector.service.control.routes import r as cr
from duetector.service.query.routes import r as qr


async def verify_token(
    server_config: Config = Depends(get_server_config),
    token: str = Depends(APIKeyQuery(name="token", auto_error=False)),
):
    if server_config.token and token != server_config.token:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")


app = FastAPI(
    title="Duetector",
    description="Data Usage Extensible Detector for data usage observability",
    version=__version__,
    dependencies=[Depends(verify_token)],
)
app.include_router(qr)
app.include_router(cr)


@app.get("/")
async def root():
    """
    Just a simple health check, returns a message.
    """
    return {"message": "Hello World"}
