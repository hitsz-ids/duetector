from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, NamedTuple, Optional

import pydantic

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

    @classmethod
    def normalize_field(cls, field, data):
        """
        Normalize field name and data
        """
        if field == "timestamp":
            field = "dt"
            data = get_boot_time_duration_ns(data)
        return field, data

    @staticmethod
    def from_namedtuple(tracer, data: NamedTuple) -> Tracking:  # type: ignore
        """
        Create a Tracking instance from tracer's data
        """
        if isinstance(tracer, type):
            tracer_name = getattr(tracer, "__name__")
        elif isinstance(tracer, str):
            tracer_name = tracer
        else:
            # Is instance of tracer
            tracer_name = getattr(tracer, "name", tracer.__class__.__name__)

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

        return Tracking(**args)


if __name__ == "__main__":
    Tracking(tracer="test", dt=datetime.now())
