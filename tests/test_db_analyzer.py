from datetime import datetime, timedelta

import pytest

from duetector.analyzer.db import DBAnalyzer
from duetector.analyzer.models import Tracking as AT
from duetector.collectors.models import Tracking as CT

now = datetime.now()

tracking_kwargs = dict(
    tracer="db_analyzer_tests",
    pid=9999,
    uid=9999,
    gid=9999,
    comm="dummy",
    cwd=None,
    fname="dummy.file",
    dt=datetime.now(),
    extended={"custom": "dummy-xargs"},
)


@pytest.fixture
def tracer_name():
    return "db_analyzer_tests"


@pytest.fixture
def collector_id():
    return "db_analyzer_tests_collector"


@pytest.fixture
def c_tracking():
    yield CT(**tracking_kwargs)


@pytest.fixture
def a_tracking():
    yield AT(**tracking_kwargs)


@pytest.fixture
def db_analyzer(full_config, c_tracking, collector_id):
    db_analyzer = DBAnalyzer(full_config)
    sessionmanager = db_analyzer.sm

    m = sessionmanager.get_tracking_model(c_tracking.tracer, collector_id)

    with sessionmanager.begin() as session:
        session.add(m(**c_tracking.model_dump(exclude=["tracer"])))
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
    assert a_tracking in db_analyzer.query(start_datetime=now - timedelta(days=1))
    assert a_tracking in db_analyzer.query(end_datetime=now + timedelta(days=1))
    assert a_tracking in db_analyzer.query(order_by_asc=["pid"])
    assert a_tracking in db_analyzer.query(order_by_desc=["pid"])

    assert len(db_analyzer.query()) == 2
    assert len(db_analyzer.query(distinct=True)) == 1

    assert AT(
        tracer=a_tracking.tracer,
        pid=a_tracking.pid,
        fname=a_tracking.fname,
    ) in db_analyzer.query(columns=["pid", "fname"])

    assert not db_analyzer.query(tracer="not-exist")
    assert not db_analyzer.query(collector_id="not-exist")
    assert not db_analyzer.query(start_datetime=now + timedelta(days=1))
    assert not db_analyzer.query(end_datetime=now - timedelta(days=1))
    assert not db_analyzer.query(start=100)
    assert not db_analyzer.query(where={"pid": 1})


# def test_brief(db_analyzer: DBAnalyzer, a_tracking, collector_id):
#     assert db_analyzer.brief()
#     # print(db_analyzer.brief())


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
