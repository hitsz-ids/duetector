from __future__ import annotations

from datetime import datetime
from typing import Any

import pydantic

from duetector.log import logger
from duetector.utils import get_boot_time_duration_ns


class Tracking(pydantic.BaseModel):
    """
    Tracking model for all tracers, bring tracer's data into a common model

    Extended fields will be stored in ``_extended`` field as a dict
    Use ``Tracking.from_namedtuple`` to create a Tracking instance from tracer's data
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
        """
        Normalize field name and data
        """
        if field == "timestamp":
            field = "dt"
            data = get_boot_time_duration_ns(data)
        return field, data

    @classmethod
    def serialize_field(cls, field, data):
        """
        Serialize filed to one of ['bool', 'str', 'bytes', 'int', 'float'] or a sequence of those types
        """
        if field == "dt":
            field = "timestamp"
            data = datetime.timestamp(data)
        return field, data

    @staticmethod
    def from_namedtuple(tracer, data: NamedTuple) -> Tracking:  # type: ignore
        """
        Create a Tracking instance from tracer's data
        """
        tracer_name = getattr(data, "tracer_name", None)
        if not tracer_name:
            if isinstance(tracer, type):
                tracer_name = getattr(tracer, "__name__")
            elif isinstance(tracer, str):
                tracer_name = tracer
            else:
                # Is instance of tracer
                tracer_name = getattr(tracer, "name", tracer.__class__.__name__)

        tracer_name = tracer_name.lower()
        args = {
            "tracer": tracer_name,
            "extended": {},
        }
        for field in data._fields:  # type: ignore
            k, v = Tracking.normalize_field(field, getattr(data, field))
            if k in Tracking.model_fields:
                args[k] = v
            else:
                args["extended"][k] = v

        if not args.get("cwd"):
            # Try get cwd from /proc/<pid>/cwd
            # Not necessary for all tracers, TODO: Add a tracer for `exec`
            try:
                args["cwd"] = open(f"/proc/{args['pid']}/cwd").read()
            except Exception:
                # Process may already exit
                pass
        try:
            return Tracking(**args)
        except ValueError as e:
            logger.error("Failed to create Tracking instance: %s", e)
            logger.exception(e)

    def set_span(self, collector, span):
        for k in self.model_fields:
            if k in ("tracer", "extended"):
                continue
            v = getattr(self, k)
            if v is not None:
                k, v = self.serialize_field(k, v)
                span.set_attribute(k, v)
        for k, v in self.extended.items():
            span.set_attribute(k, v)
        span.set_attribute("collector_id", collector.id)


if __name__ == "__main__":
    Tracking(tracer="test", dt=datetime.now())
