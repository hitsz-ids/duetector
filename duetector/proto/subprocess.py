from __future__ import annotations

import json
from collections import namedtuple
from typing import Any, Dict

from pydantic import BaseModel

from duetector.log import logger

VERSION = "0.1.0"


class Message(BaseModel):
    proto: str
    version: str = VERSION
    type: str
    payload: Dict[str, Any] = {}

    @classmethod
    def from_host(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def from_subprocess(cls, *args, **kwargs):
        raise NotImplementedError

    def serialize_namedtuple(self):
        return namedtuple("EventPayload", self.payload)(**self.payload)


def dispatch_message(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid json: {data}")
            return None

    if data["type"] == "init":
        return InitMessage.from_subprocess(data)
    elif data["type"] == "event":
        return EventMessage.from_subprocess(data.get("payload", {}))
    elif data["type"] == "stopped":
        return StoppedMessage.from_subprocess(data)
    else:
        raise ValueError(f"Unknown message type: {data['type']}")


class InitMessage(Message):
    proto: str = "duetector"
    version: str = "0.1.0"
    type: str = "init"
    payload: Dict[str, Any] = {}

    @classmethod
    def from_host(cls, host, tracer) -> InitMessage:
        return InitMessage(
            payload={
                "poll_time": host.timeout,
                "kill_timeout": host.kill_timeout,
                "config": tracer.config._config_dict,
            }
        )

    @classmethod
    def from_subprocess(cls, data) -> InitMessage:
        return InitMessage(payload=data)


class EventMessage(Message):
    proto: str = "duetector"
    version: str = "0.1.0"
    type: str = "event"
    payload: Dict[str, Any] = {}

    @classmethod
    def from_host(cls, *args, **kwargs) -> EventMessage:
        return EventMessage()

    @classmethod
    def from_subprocess(cls, data) -> EventMessage:
        if isinstance(data, str):
            data = json.loads(data)

        return EventMessage(payload=data)


class StopMessage(Message):
    proto: str = "duetector"
    version: str = "0.1.0"
    type: str = "stop"
    payload: Dict[str, Any] = {}

    @classmethod
    def from_host(cls, *args, **kwargs) -> StopMessage:
        return StopMessage()


class StoppedMessage(StopMessage):
    type: str = "stopped"

    @classmethod
    def from_subprocess(cls, *args, **kwargs) -> StoppedMessage:
        return StoppedMessage()
