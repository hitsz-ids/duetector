from fastapi import APIRouter, Depends

from duetector.service.config import get_config

r = APIRouter(
    prefix="/control",
    tags=["control"],
)


@r.get("/")
async def root(config: dict = Depends(get_config)):
    pass
