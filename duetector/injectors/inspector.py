from __future__ import annotations

import glob
import itertools
import signal
from threading import Event, Thread
from typing import Any

import pydantic
from watchfiles import Change, DefaultFilter, _rust_notify, watch

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

from duetector.log import logger
from duetector.utils import Singleton


class ProcInfo(pydantic.BaseModel):
    pass


class PidFilter(DefaultFilter):
    @classmethod
    def get_pid(cls, path: str) -> str:
        return path.split("/")[-1]

    def __call__(self, change: Change, path: str) -> bool:
        return super().__call__(change, path) and self.get_pid(path).isnumeric()


class ProcWatcher(metaclass=Singleton):
    def __init__(
        self,
        proc_dir: str = "/proc",
        ignore_permission_denied: bool = True,
    ) -> None:
        self.proc_dir = proc_dir
        self.ignore_permission_denied = ignore_permission_denied

        self._cache: dict[int, ProcInfo] = {}
        self.thread: Thread | None = None

        self.stop_event = Event()
        self.stop_event.clear()

        self.start()
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def _sync(self):
        logger.debug("Force sync proc cache.")
        pids = [
            int(PidFilter.get_pid(path))
            for path in glob.glob(f"{self.proc_dir.rstrip('/')}/[0-9]*")
        ]
        for pid in pids:
            if pid not in self._cache:
                self.add_cache(pid)
        for cached_pid in self._cache.keys():
            if cached_pid not in pids:
                self.remove_cache(cached_pid)

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
                except _rust_notify.WatchfilesRustInternalError as e:
                    self._sync()
                except Exception as e:
                    logger.exception(e)
                if self.stop_event.is_set():
                    return

        self.thread = Thread(
            target=_,
        )
        self.thread.start()
        self._sync()
        logger.info("Proc watcher started.")

    def _watch(self):
        for changes in watch(
            self.proc_dir,
            watch_filter=PidFilter(),
            stop_event=self.stop_event,
            ignore_permission_denied=self.ignore_permission_denied,
            recursive=False,
            poll_delay_ms=300,
            force_polling=True,
        ):
            for change, path in changes:
                pid = int(PidFilter.get_pid(path))
                if change == Change.added:
                    self.add_cache(pid)
                elif change == Change.deleted:
                    self.remove_cache(pid)

    def get(self, pid: int) -> ProcInfo | None:
        return self._cache.get(pid)

    def add_cache(self, pid: int):
        if pid in self._cache:
            return
        # TODO: Cache it
        logger.debug(f"Add proc cache for `{pid}`")
        pass

    def remove_cache(self, pid: int, delay=1):
        if not delay:
            logger.debug(f"Remove proc cache for `{pid}` now")
            return self._cache.pop(pid, None)
        # TODO: Schedule remove cache after 1 seconds
        logger.debug(f"Remove proc cache for `{pid}` after {delay} seconds")

    def stop(self, sig=None, frame=None):
        self.stop_event.set()
        self._cache.clear()
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
    @cache
    def id(self) -> str:
        return with_prefix(self.sep, self.prefix, self.name or self.__class__.__name__)

    @cache
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
    @cache
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
    @cache
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
