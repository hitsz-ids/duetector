from __future__ import annotations

import itertools
import signal
from threading import Event, Thread
from typing import Any

from watchfiles import watch

from duetector.log import logger
from duetector.utils import Singleton


class ProcWatcher(metaclass=Singleton):
    def __init__(
        self,
        proc_dir: str = "/proc",
        ignore_permission_denied: bool = True,
    ) -> None:
        self.proc_dir = proc_dir
        self.ignore_permission_denied = ignore_permission_denied

        self.thread: Thread | None = None

        self.stop_event = Event()
        self.stop_event.clear()

        self.start()
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def start(self):
        if self.thread:
            if self.thread.is_alive():
                return
            else:
                self.stop()

        self.stop_event.clear()

        def _():
            logger.debug("Starting watch proc dir.")
            while True:
                try:
                    self._watch()
                except Exception as e:
                    logger.exception(e)
                self.stop_event.wait(0.001)
                if self.stop_event.is_set():
                    return

        self.thread = Thread(
            target=_,
        )
        self.thread.start()
        logger.info("Proc watcher started.")

    def _watch(self):
        for changes in watch(
            self.proc_dir,
            stop_event=self.stop_event,
            ignore_permission_denied=self.ignore_permission_denied,
            recursive=False,
            force_polling=True,
        ):
            pass
            # logger.info(changes)

    def stop(self, sig=None, frame=None):
        self.stop_event.set()
        if self.thread:
            logger.info("Waiting proc watcher to stop.")
            self.thread.join(1)
            self.thread = None

    def pause(self):
        signal.pause()


def with_prefix(sep: str, prefix, key: str | list[str]) -> str:
    if isinstance(key, str):
        return sep.join([prefix, key.lower()])
    else:
        return sep.join(itertools.chain([prefix], [k.lower() for k in key]))


class Inspector:
    sep = "__"
    prefix = "inspector"
    name = None

    @property
    def id(self) -> str:
        return with_prefix(self.sep, self.prefix, self.name or self.__class__.__name__)

    def with_id(self, key: str | list[str]) -> str:
        return with_prefix(self.sep, self.id, key)

    def is_inspected(self, model: dict[str, Any]):
        return self.id in model and model[self.id]

    def _mark_inspected(self, model: dict[str, Any]) -> None:
        model[self.id] = True

    def _ensure_with_id(self, model: dict[str, Any]) -> dict[str, Any]:
        return {self.with_id(k) if not k.startswith(self.id) else k: v for k, v in model.items()}

    def inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        if self.is_inspected(model):
            return {}

        inspect_info = self._inspect(model)
        inspect_info = self._ensure_with_id(inspect_info)
        self._mark_inspected(inspect_info)

        return inspect_info

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def stop(self):
        pass


class NamespaceInspector(Inspector):
    @property
    def name(self) -> str:
        return self.sep.join(["proc", "namespace"])

    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}

    def stop(self):
        self.proc_watcher.stop()


class CgroupInspector(Inspector):
    @property
    def name(self) -> str:
        return self.sep.join(["proc", "cgroup"])

    def __init__(self) -> None:
        self.proc_watcher = ProcWatcher()

    def _inspect(self, model: dict[str, Any]) -> dict[str, Any]:
        return {}

    def stop(self):
        self.proc_watcher.stop()


if __name__ == "__main__":
    w = ProcWatcher()
    w.pause()
