import os

import pytest

from duetector.injectors.inspector import (
    CgroupInspector,
    NamespaceInspector,
    ProcInfo,
    ProcWatcher,
)


@pytest.fixture(scope="session")
def proc_watcher():
    p = ProcWatcher()
    try:
        yield p
    finally:
        p.stop()


@pytest.fixture
def model():
    yield {"pid": os.getpid()}


def test_proc_info_from_pid():
    proc_info = ProcInfo.from_pid(os.getpid())
    assert proc_info
    assert proc_info.pid
    assert proc_info.cwd
    assert proc_info.exe
    assert proc_info.root
    assert proc_info.ns
    assert proc_info.cgroups


def test_proc_watcher(proc_watcher: ProcWatcher):
    assert proc_watcher.get(os.getpid())


@pytest.mark.parametrize("Inspector", [NamespaceInspector, CgroupInspector])
def test_ns_inspector(Inspector, model):
    i = Inspector()
    extra = i.inspect(model)
    assert i.is_inspected(extra)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
