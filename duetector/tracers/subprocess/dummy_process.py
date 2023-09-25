#!/usr/bin/env python

# TODO: Implement a dummy process that can be used to test the tracer

import json
import signal
import threading
import time


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

    def stop(self, *args, **kwargs):
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
    signal.signal(signal.SIGINT, t.stop)
    signal.signal(signal.SIGTERM, t.stop)
    signal.pause()


if __name__ == "__main__":
    main()
