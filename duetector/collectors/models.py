from __future__ import annotations

from typing import Dict, NamedTuple, Optional

import pydantic


class Tracking(pydantic.BaseModel):
    """
    Tracking model for all tracers, bring tracer's data into a common model

    Extended fields will be stored in `extended` field as a dict
    Use Tracking.from_namedtuple to create a Tracking instance from tracer's data
    """

    tracer: str

    pid: Optional[int] = None
    uid: Optional[int] = None
    gid: Optional[int] = None
    comm: Optional[str] = "Unknown"
    cwd: Optional[str] = None
    fname: Optional[str] = None
    timestamp: Optional[int] = None

    extended: Dict[str, str] = {}

    @staticmethod
    def from_namedtuple(tracer, data: NamedTuple) -> Tracking:  # type: ignore
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
            if field in Tracking.model_fields:
                args[field] = getattr(data, field)
            else:
                args["extended"][field] = getattr(data, field)

        if not args.get("cwd"):
            # Try get cwd from /proc/<pid>/cwd
            # Not necessary for all tracers, TODO: Add a tracer for `exec`
            try:
                args["cwd"] = open(f"/proc/{args['pid']}/cwd").read()
            except Exception:
                # Process may already exit
                pass

        return Tracking(**args)
