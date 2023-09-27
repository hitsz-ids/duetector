#!/usr/bin/env python

import json
import os
import signal
import threading
from sys import stderr, stdout
from typing import IO

from duetector.proto.subprocess import (
    EventMessage,
    InitMessage,
    StopMessage,
    StoppedMessage,
)


def _writeline(msg, io: IO = stdout):
    if not msg.endswith("\n"):
        msg += "\n"
    io.write(msg)
    io.flush()


class Tracer:
    def __init__(self, init_config) -> None:
        self.name = "dummy"
        self.version = "0.1.0"
        self.event = threading.Event()
        self.thread = None
        self.init_config = init_config
        self.timewait = 1

    def _target(self):
        msg = EventMessage.from_subprocess(
            {
                "pid": os.getpid(),
                "extra": "noting",
            }
        )
        while not self.event.is_set():
            _writeline(msg.model_dump_json())
            self.event.wait(self.timewait)

    def start(self):
        if self.thread and self.thread.is_alive():
            raise RuntimeError("Treacer already running")
        msg = InitMessage.from_subprocess({"name": self.name, "version": self.version})
        _writeline(msg.model_dump_json())
        self.event.clear()
        self.thread = threading.Thread(target=self._target)
        self.thread.start()

    def stop(self):
        self.event.set()
        self.thread.join()
        self.thread = None


def dispatch_message(data):
    if isinstance(data, str):
        data = json.loads(data)

    if data["type"] == "init":
        return InitMessage(payload=data)
    elif data["type"] == "event":
        return EventMessage(payload=data)
    elif data["type"] == "stop":
        return StopMessage(payload=data)
    else:
        raise ValueError(f"Unknown message type: {data['type']}")


def main():
    line = input()
    msg = dispatch_message(line)
    if isinstance(msg, InitMessage):
        init_config = msg.payload
        t = Tracer(init_config)
        t.start()
    else:
        raise ValueError("Expect init message")

    def _stop(*args, **kwargs):
        t.stop()
        _writeline(StoppedMessage().model_dump_json())
        exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    while True:
        line = input()
        msg = dispatch_message(line)
        if isinstance(msg, EventMessage):
            stderr.write(msg.serialize_namedtuple())
        if isinstance(msg, StopMessage):
            # Send stop signal to itself
            os.kill(os.getpid(), signal.SIGTERM)
        if isinstance(msg, InitMessage):
            raise ValueError("Unexpected init message")


if __name__ == "__main__":
    main()
