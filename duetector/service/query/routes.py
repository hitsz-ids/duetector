from fastapi import APIRouter, Body, Depends

from duetector.service.base import get_controller
from duetector.service.query.controller import AnalyzerController
from duetector.service.query.models import (
    AvaliableAnalyzers,
    BriefResult,
    QueryBody,
    QueryResult,
)
from duetector.service.utils import ensure_async

r = APIRouter(
    prefix="/query",
    tags=["query"],
)


@r.get("/", response_model=AvaliableAnalyzers)
async def root(
    controller: AnalyzerController = Depends(get_controller(AnalyzerController)),
):
    """
    Response available analyzer
    """
    return AvaliableAnalyzers(analyzers=controller.avaliable_analyzer_names)


@r.post("/{analyzer_name}", response_model=QueryResult)
async def query(
    analyzer_name: str,
    query_param: QueryBody = Body(default=QueryBody(collector_id="unknown-collector-id")),
    controller: AnalyzerController = Depends(get_controller(AnalyzerController)),
):
    """
    Query data from analyzer
    """
    analyzer = controller.get_analyzer(analyzer_name)
    query_param = controller.wrap_query_param(query_param)
    trackings = await ensure_async(analyzer.query, **query_param)

    return QueryResult(
        trackings=trackings,
        count=len(trackings),
    )


@r.get("/{analyzer_name}/brief", response_model=BriefResult)
async def query_brief(
    analyzer_name: str,
    controller: AnalyzerController = Depends(get_controller(AnalyzerController)),
):
    # type is not serializable, so we need to get analyzer without inspect type
    analyzer = controller.get_analyzer(analyzer_name)
    brief = await ensure_async(analyzer.brief, inspect_type=False)
    return BriefResult(
        brief=brief,
        analyzer_name=analyzer_name,
    )
