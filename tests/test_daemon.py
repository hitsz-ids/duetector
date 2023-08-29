import pytest

from duetector.tools.daemon import Daemon


@pytest.fixture
def daemon():
    yield Daemon(
        cmd=["sleep", "100"],
        workdir="/tmp/duetector",
        env_dict={"DUETECTOR_LOG_LEVEL": "DEBUG"},
    )


def test_daemon(daemon):
    daemon.start()
    assert daemon.pid
    assert daemon.poll()
    daemon.stop()
    assert not daemon.pid
    assert not daemon.poll()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
