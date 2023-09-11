import pytest

from duetector.analyzer.db import DBAnalyzer
from duetector.analyzer.models import Tracking as AT
from duetector.collectors.models import Tracking as CT


@pytest.fixture
def tracer_name():
    return "db_analyzer_tests"


@pytest.fixture
def collector_id():
    return "db_analyzer_tests_collector"


@pytest.fixture
def c_tracking(tracer_name):
    yield CT(
        tracer=tracer_name,
    )


@pytest.fixture
def a_tracking(tracer_name):
    yield AT(
        tracer=tracer_name,
    )


@pytest.fixture
def db_analyzer(full_config, c_tracking, collector_id):
    db_analyzer = DBAnalyzer(full_config)
    sessionmanager = db_analyzer.sm

    m = sessionmanager.get_tracking_model(c_tracking.tracer, collector_id)

    with sessionmanager.begin() as session:
        session.add(m(**c_tracking.model_dump(exclude=["tracer"])))
        session.commit()

    assert sessionmanager.inspect_all_tables() == [
        sessionmanager.get_table_names(c_tracking.tracer, collector_id)
    ]
    assert sessionmanager.inspect_all_tables("not-exist") == []
    yield db_analyzer


def test_query(db_analyzer: DBAnalyzer, a_tracking, collector_id):
    assert a_tracking in db_analyzer.query()
    assert a_tracking in db_analyzer.query(tracer=a_tracking.tracer)
    assert a_tracking in db_analyzer.query(collector_id=collector_id)
    assert a_tracking in db_analyzer.query(tracer=a_tracking.tracer, collector_id=collector_id)

    assert not db_analyzer.query(tracer="not-exist")
    assert not db_analyzer.query(collector_id="not-exist")


def test_brief(db_analyzer: DBAnalyzer, a_tracking, collector_id):
    assert db_analyzer.brief()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
