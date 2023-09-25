#!/usr/bin/env python

# TODO: Implement a dummy process that can be used to test the tracer

import json
import signal
import threading
import time
from sys import stderr


class Tracer:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.thread = None

    def _target(self):
        msg = {"version": "v0", "event": "do_something", "payload": {}}
        while not self.event.is_set():
            print(json.dumps(msg))
            self.event.wait(1)

    def start(self):
        if self.thread and self.thread.is_alive():
            raise RuntimeError("Treacer already running")

        self.event.clear()
        self.thread = threading.Thread(target=self._target)

        msg = {
            "version": "v0",
            "event": "init",
            "payload": {},
        }
        print(json.dumps(msg))
        self.thread.start()

    def stop(self):
        self.event.set()
        self.thread.join()
        self.thread = None

        msg = {
            "version": "v0",
            "event": "stopped",
            "payload": {},
        }
        print(json.dumps(msg))


def main():
    t = Tracer()
    t.start()

    def _stop(*args, **kwargs):
        t.stop()
        exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    while True:
        line = input()
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            msg = {
                "version": "v0",
                "event": "error",
                "payload": {"error": str(e)},
            }
        stderr.write(json.dumps(msg))


if __name__ == "__main__":
    main()
