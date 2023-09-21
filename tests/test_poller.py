import time

import pytest

from duetector.tools.poller import Poller


@pytest.fixture
def config():
    yield {
        "poller": {
            "interval_ms": 500,
            "call_when_shutdown": False,
        }
    }


@pytest.fixture
def config_with_call_when_shutdown():
    yield {
        "poller": {
            "interval_ms": 500,
            "call_when_shutdown": True,
        }
    }


@pytest.fixture
def poller(config):
    return Poller(config)


@pytest.fixture
def poller_with_call_when_shutdown(config_with_call_when_shutdown):
    return Poller(config_with_call_when_shutdown)


def test_poller(poller: Poller, capsys):
    poller.start(lambda: print("hello"))
    time.sleep(poller.interval_ms / 1000 * 1.5)
    poller.shutdown()
    poller.wait()
    captured = capsys.readouterr()
    assert captured.out == "hello\nhello\n"


def test_poller_with_call_when_shutdown(poller_with_call_when_shutdown: Poller, capsys):
    poller_with_call_when_shutdown.start(lambda: print("hello"))
    time.sleep(poller_with_call_when_shutdown.interval_ms / 1000 * 1.5)
    poller_with_call_when_shutdown.shutdown()
    poller_with_call_when_shutdown.wait()
    captured = capsys.readouterr()
    assert captured.out == "hello\nhello\nhello\n"


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
