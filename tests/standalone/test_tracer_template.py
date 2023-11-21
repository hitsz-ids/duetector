import pytest

from duetector.managers.tracer import ShellTracer, TracerTemplate


def test_disabled_property():
    tracer_template = TracerTemplate({"disabled": True})
    assert tracer_template.disabled == True

    tracer_template = TracerTemplate({"disabled": False})
    assert tracer_template.disabled == False


def test_init():
    tracer_template = TracerTemplate({"disabled": True})
    assert tracer_template.init() == []

    tracer_template = TracerTemplate(
        {
            "disabled": False,
            "sh": {
                "tracer_name": {
                    "comm": ["ps", "-aux"],
                    "config": {"enable_cache": False},
                }
            },
        }
    )
    tracers = tracer_template.init()
    assert len(tracers) == 1
    assert isinstance(tracers[0], ShellTracer)


def test_get_wrap_tracer():
    tracer_template = TracerTemplate()
    tracer = tracer_template._get_wrap_tracer(
        "sh", "tracer_name", {"comm": ["ps", "-aux"], "config": {"enable_cache": False}}
    )
    assert isinstance(tracer, ShellTracer)
    assert tracer.config._config_dict == {"disabled": False, "enable_cache": False}
    assert tracer.comm == ["ps", "-aux"]


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
