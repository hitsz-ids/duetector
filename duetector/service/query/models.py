from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from duetector.analyzer.models import AnalyzerBrief, Tracking


class AvaliableAnalyzers(BaseModel):
    analyzers: List[str]


class QueryBody(BaseModel):
    tracers: Optional[List[str]] = None
    collector_ids: Optional[List[str]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    start: int = 0
    limit: int = 0
    columns: Optional[List[str]] = None
    where: Optional[Dict[str, Any]] = None
    distinct: bool = False
    order_by_asc: Optional[List[str]] = None
    order_by_desc: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tracers": [],
                    "collector_ids": [],
                    "start_datetime": datetime.fromtimestamp(0),
                    "end_datetime": datetime.now(),
                    "start": 0,
                    "limit": 0,
                    "columns": [],
                    "where": {},
                    "distinct": False,
                    "order_by_asc": [],
                    "order_by_desc": [],
                }
            ]
        }
    }


class QueryResult(BaseModel):
    trackings: List[Tracking]
    count: int


class BriefResult(BaseModel):
    brief: AnalyzerBrief
    analyzer_name: str
