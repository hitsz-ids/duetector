import pytest


@pytest.fixture
def sh_monitor(full_config):
    from duetector.monitors.sh_monitor import ShMonitor

    return ShMonitor(full_config)


def test_sh_monitor(sh_monitor):
    assert sh_monitor
    assert sh_monitor.tracers
    assert sh_monitor.filters
    assert sh_monitor.collectors
    assert sh_monitor.host
    assert sh_monitor.auto_init
    assert sh_monitor.timeout
    sh_monitor.poll_all()
    sh_monitor.shutdown()
    assert sh_monitor.summary()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
