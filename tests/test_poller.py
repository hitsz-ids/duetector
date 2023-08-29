import time

import pytest

from duetector.tools.poller import Poller


@pytest.fixture
def config():
    yield {
        "poller": {
            "interval_ms": 500,
        }
    }


@pytest.fixture
def poller(config):
    return Poller(config)


def test_poller(poller: Poller, capsys):
    poller.start(lambda: print("hello"))
    time.sleep(poller.interval_ms / 1000 * 1.5)
    poller.shutdown()
    poller.wait()
    captured = capsys.readouterr()
    assert captured.out == "hello\nhello\n"


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
