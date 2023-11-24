from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from duetector.analyzer.models import AnalyzerBrief, Tracking


class AvaliableAnalyzers(BaseModel):
    analyzers: list[str]


class QueryBody(BaseModel):
    collector_id: str
    tracers: list[str] | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    start: int = 0
    limit: int = 0
    columns: list[str] | None = None
    where: dict[str, Any] = None
    distinct: bool = False
    order_by_asc: list[str] | None = None
    order_by_desc: list[str] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tracers": [],
                    "collector_id": "test-service",
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
    trackings: list[Tracking]
    count: int


class BriefResult(BaseModel):
    brief: AnalyzerBrief
    analyzer_name: str
