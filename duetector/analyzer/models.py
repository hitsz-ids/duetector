from __future__ import annotations

from datetime import datetime
from typing import Any

import pydantic

from duetector.analyzer.jaeger.proto import model_pb2 as JModel
from duetector.analyzer.jaeger.proto.model_pb2 import Span as JSpan


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

    pid: int | None = None
    """
    Process ID
    """
    uid: int | None = None
    """
    User ID
    """
    gid: int | None = None
    """
    Group ID of user
    """
    comm: str | None = "Unknown"
    """
    Command name
    """
    cwd: str | None = None
    """
    Current working directory of process
    """
    fname: str | None = None
    """
    File name which is being accessed
    """

    dt: datetime | None = None
    """
    datetime of event
    """

    extended: dict[str, Any] = {}
    """
    Extended fields, will be stored in ``extended`` field as a dict
    """

    @classmethod
    def normalize_field(cls, field, data):
        if field == "timestamp":
            field = "dt"
            data = datetime.fromtimestamp(data)
        return field, data

    @classmethod
    def from_jaeger_span(cls, tracer_name, span: JSpan) -> "Tracking":
        value_type_to_field_attr = {
            JModel.STRING: "v_str",
            JModel.BOOL: "v_bool",
            JModel.INT64: "v_int64",
            JModel.FLOAT64: "v_float64",
            JModel.BINARY: "v_binary",
        }

        t = Tracking(tracer=tracer_name)
        for msg in span.tags:
            field = msg.key
            data = getattr(msg, value_type_to_field_attr[msg.v_type])
            field, data = Tracking.normalize_field(field, data)
            if field in Tracking.model_fields:
                setattr(t, field, data)
            else:
                t.extended[field] = data

        return t


class Brief(pydantic.BaseModel):
    """
    Brief of a tracking set, mostly a table.
    """

    tracer: str
    collector_id: str
    start: datetime | None = None
    end: datetime | None = None
    count: int | None = None
    fields: dict[str, Any] = {}

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

    tracers: set[str]
    """
    Set of tracers
    """

    collector_ids: set[str]
    """
    Set of collector ids
    """

    briefs: dict[str, Brief]

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
