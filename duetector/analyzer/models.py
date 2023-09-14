from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

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
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    count: Optional[int] = None
    fields: Dict[str, Any] = {}

    def __repr__(self):
        fields_repr = ", ".join([f"{k}: {v}" for k, v in self.fields.items()])

        s = f"""
{self.tracer}@{self.collector_id} with {self.count} records
from {self.start} to {self.end}
available fields: [{fields_repr}]
"""

        return s

    def __str__(self):
        return self.__repr__()


class AnalyzerBrief(pydantic.BaseModel):
    """
    Brief of analyzer.
    """

    tracers: Set[str]
    """
    Set of tracers
    """

    collector_ids: Set[str]
    """
    Set of collector ids
    """

    briefs: Dict[str, Brief]

    def __repr__(self):
        briefs_repr = "\n".join(
            [f"\n----------------{b}----------------" for b in self.briefs.values()]
        )
        s = f"""
Available tracers: {self.tracers}
Available collector ids: {self.collector_ids}
briefs: {briefs_repr}
"""
        return s

    def __str__(self):
        return self.__repr__()
