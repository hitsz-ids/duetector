import pytest

from duetector.analyzer.db import DBAnalyzer
from duetector.collectors.models import Tracking


@pytest.fixture
def tracer_name():
    return "db_analyzer_tests"


@pytest.fixture
def collector_id():
    return "db_analyzer_tests_collector"


@pytest.fixture
def tracking(tracer_name):
    yield Tracking(
        tracer=tracer_name,
    )


@pytest.fixture
def db_analyzer(full_config, tracking, collector_id):
    db_analyzer = DBAnalyzer(full_config)
    sessionmanager = db_analyzer.sm

    m = sessionmanager.get_tracking_model(tracking.tracer, collector_id)

    with sessionmanager.begin() as session:
        session.add(m(**tracking.model_dump(exclude=["tracer"])))
        session.commit()

    assert sessionmanager.inspect_all_tables() == [
        sessionmanager.get_table_names(tracking.tracer, collector_id)
    ]
    assert sessionmanager.inspect_all_tables("not-exist") == []
    yield db_analyzer


def test_query_all(db_analyzer: DBAnalyzer, tracking, collector_id):
    assert tracking in db_analyzer.query_all()
    assert tracking in db_analyzer.query_all(tracer=tracking.tracer)
    assert tracking in db_analyzer.query_all(collector_id=collector_id)
    assert tracking in db_analyzer.query_all(tracer=tracking.tracer, collector_id=collector_id)

    assert not db_analyzer.query_all(tracer="not-exist")
    assert not db_analyzer.query_all(collector_id="not-exist")


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
