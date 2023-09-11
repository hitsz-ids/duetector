from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pydantic


class Tracking(pydantic.BaseModel):
    """
    Tracking model for analyzer.

    Currently, this is a copy of ``duetector.collectors.models.Tracking``.
    And as an ACL(anti-corruption layer), we will not use ``duetector.collectors.models.Tracking`` directly.
    """

    tracer: str
    """
    Tracer's name
    """

    pid: Optional[int] = None
    """
    Process ID
    """
    uid: Optional[int] = None
    """
    User ID
    """
    gid: Optional[int] = None
    """
    Group ID of user
    """
    comm: Optional[str] = "Unknown"
    """
    Command name
    """
    cwd: Optional[str] = None
    """
    Current working directory of process
    """
    fname: Optional[str] = None
    """
    File name which is being accessed
    """

    dt: Optional[datetime] = None
    """
    datetime of event
    """

    extended: Dict[str, Any] = {}
    """
    Extended fields, will be stored in ``extended`` field as a dict
    """


class Brief(pydantic.BaseModel):
    """
    Brief of a tracking set, mostly a table.
    """

    tracer: str
    collector_id: str
    start: Optional[datetime]
    end: Optional[datetime]
    count: int


class AnalyzerBrief(pydantic.BaseModel):
    """
    Brief of analyzer.
    """

    tracers: List[str]
    """
    List of tracers
    """

    collector_ids: List[str]
    """
    List of collector ids
    """

    briefs: List[Brief]
