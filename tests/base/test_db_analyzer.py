import os
from datetime import datetime, timedelta

import pytest

from duetector.analyzer.db import DBAnalyzer
from duetector.analyzer.models import Tracking as AT
from duetector.collectors.models import Tracking as CT
from duetector.managers.analyzer import AnalyzerManager

now = datetime.now()

tracking_kwargs = dict(
    tracer="db_analyzer_tests",
    pid=os.getpid(),
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
def config(full_config):
    yield AnalyzerManager(full_config).config._config_dict


@pytest.fixture
def db_analyzer(config, c_tracking, collector_id):
    db_analyzer = DBAnalyzer(config)
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


async def test_query(db_analyzer: DBAnalyzer, a_tracking, collector_id):
    assert a_tracking in await db_analyzer.query()
    assert a_tracking in await db_analyzer.query(tracers=[a_tracking.tracer])
    assert a_tracking in await db_analyzer.query(collector_ids=[collector_id])
    assert a_tracking in await db_analyzer.query(
        tracers=[a_tracking.tracer], collector_ids=[collector_id]
    )
    assert a_tracking in await db_analyzer.query(start_datetime=now - timedelta(days=1))
    assert a_tracking in await db_analyzer.query(end_datetime=now + timedelta(days=1))
    assert a_tracking in await db_analyzer.query(order_by_asc=["pid"])
    assert a_tracking in await db_analyzer.query(order_by_desc=["pid"])

    assert len(await db_analyzer.query()) == 2
    assert len(await db_analyzer.query(distinct=True)) == 1

    assert AT(
        tracer=a_tracking.tracer,
        pid=a_tracking.pid,
        fname=a_tracking.fname,
    ) in await db_analyzer.query(columns=["pid", "fname"])

    assert not await db_analyzer.query(tracers=["not-exist"])
    assert not await db_analyzer.query(collector_ids=["not-exist"])
    assert not await db_analyzer.query(start_datetime=now + timedelta(days=1))
    assert not await db_analyzer.query(end_datetime=now - timedelta(days=1))
    assert not await db_analyzer.query(start=100)
    assert not await db_analyzer.query(where={"pid": 1})


async def test_brief(db_analyzer: DBAnalyzer, a_tracking, collector_id):
    assert await db_analyzer.brief()
    assert await db_analyzer.brief(tracers=[a_tracking.tracer])
    assert await db_analyzer.brief(collector_ids=[collector_id])
    assert await db_analyzer.brief(tracers=[a_tracking.tracer], collector_ids=[collector_id])
    assert await db_analyzer.brief(start_datetime=now - timedelta(days=1))
    assert await db_analyzer.brief(end_datetime=now + timedelta(days=1))
    assert await db_analyzer.brief(with_details=False)
    assert await db_analyzer.brief(distinct=True)

    assert not (await db_analyzer.brief(tracers=["not-exist"])).tracers
    assert not (await db_analyzer.brief(collector_ids=["not-exist"])).collector_ids
    assert not list(
        (await db_analyzer.brief(start_datetime=now + timedelta(days=1))).briefs.values()
    )[0].count
    assert not list(
        (await db_analyzer.brief(end_datetime=now - timedelta(days=1))).briefs.values()
    )[0].count


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
