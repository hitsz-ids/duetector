from fastapi import APIRouter, Depends

from duetector.service.base import get_controller
from duetector.service.config import get_config
from duetector.service.query.controller import AnalyzerController

r = APIRouter(
    prefix="/query",
)


@r.get("/")
async def root(config: dict = Depends(get_config)):
    return config


@r.get("/who")
async def who(controller: AnalyzerController = Depends(get_controller(AnalyzerController))):
    return str(controller.analyzer)
