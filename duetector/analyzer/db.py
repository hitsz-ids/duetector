from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select

from duetector.analyzer.base import Analyzer
from duetector.analyzer.models import AnalyzerBrief, Brief, Tracking
from duetector.db import SessionManager


class DBAnalyzer(Analyzer):
    """
    A analyzer using database.

    As a top model, it will init a ``SessionManager`` and pass it to submodels.

    Config scope is ``db_analyzer``.

    Example:

        .. code-block:: python

            from duetector.analyzer.db import DBAnalyzer
            from duetector.analyzer.models import Tracking as AT
            from duetector.collectors.models import Tracking as CT


            collector_id = "db_analyzer_tests_collector"
            c_tracking = CT(
                tracer="t",
            )
            db_analyzer = DBAnalyzer()
            m = db_analyzer.sm.get_tracking_model(c_tracking.tracer, collector_id)
            with db_analyzer.sm.begin() as session:
                session.add(m(**c_tracking.model_dump(exclude=["tracer"])))
                session.commit()

            a_tracking = AT(
                tracer=c_tracking.tracer,
            )
            assert a_tracking in db_analyzer.query()
            assert a_tracking in db_analyzer.query(tracer=a_tracking.tracer)
            assert a_tracking in db_analyzer.query(collector_id=collector_id)
            assert a_tracking in db_analyzer.query(
                    tracer=a_tracking.tracer, collector_id=collector_id
            )
            assert not db_analyzer.query(tracer="not-exist")
            assert not db_analyzer.query(collector_id="not-exist")

    Note:
        Currently, it will **NOT** be configured by ``DBcollector``'s config,
        as we design it to be a standalone model.
    """

    default_config = {
        **Analyzer.default_config,
        "db": {
            **SessionManager.default_config,
            "engine": {
                "url": "sqlite:///duetector-dbcollector.sqlite3",
            },
        },
    }
    """
    Default config for ``DBAnalyzer``.
    """

    config_scope = "db_analyzer"
    """
    Config scope for this analyzer.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel
        self.sm: SessionManager = SessionManager(self.config._config_dict)

    def query(
        self,
        tracer: Optional[str] = None,
        collector_id: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start: int = 0,
        limit: int = 0,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        distinct: bool = False,
        order_by_asc: Optional[List[str]] = None,
        order_by_desc: Optional[List[str]] = None,
    ) -> List[Tracking]:
        """
        Query all tracking records from database.

        Args:
            tracer (Optional[str], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_id (Optional[str], optional): Collector id. Defaults to None, all collector id will be queried.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            start (int, optional): Start index. Defaults to 0.
            limit (int, optional): Limit of records. Defaults to 20. ``0`` means no limit.
            columns (Optional[List[str]], optional): Columns to query. Defaults to None, all columns will be queried.
            where (Optional[Dict[str, Any]], optional): Where clause. Defaults to None.
            distinct (bool, optional): Distinct. Defaults to False.
            order_by_asc (Optional[List[str]], optional): Order by asc. Defaults to None.
            order_by_desc (Optional[List[str]], optional): Order by desc. Defaults to None.
        Returns:
            List[duetector.analyzer.models.Tracking]: List of tracking records.

        """

        tables = self.sm.inspect_all_tables()
        if tracer:
            tables = [t for t in tables if self.sm.table_name_to_tracer(t) == tracer]
        if collector_id:
            tables = [t for t in tables if self.sm.table_name_to_collector_id(t) == collector_id]

        r = []
        for t in tables:
            tracer = self.sm.table_name_to_tracer(t)
            collector_id = self.sm.table_name_to_collector_id(t)
            m = self.sm.get_tracking_model(tracer, collector_id)

            columns = columns or m.inspect_fields().keys()
            statm = select(*[getattr(m, k) for k in columns]).offset(start)
            if start_datetime:
                statm = statm.where(m.dt >= start_datetime)
            if end_datetime:
                statm = statm.where(m.dt <= end_datetime)
            if limit:
                statm = statm.limit(limit)
            if where:
                statm = statm.where(*[getattr(m, k) == v for k, v in where.items()])
            if distinct:
                statm = statm.distinct()
            if order_by_asc:
                statm = statm.order_by(*[getattr(m, k).asc() for k in order_by_asc])
            if order_by_desc:
                statm = statm.order_by(*[getattr(m, k).desc() for k in order_by_desc])

            with self.sm.begin() as session:
                r.extend(
                    [
                        Tracking(tracer=tracer, **{k: v for k, v in zip(columns, r)})
                        for r in session.execute(statm).fetchall()
                    ]
                )

        return r

    def get_all_tracers(self) -> List[str]:
        """
        Get all tracers from database.

        Returns:
            List[str]: List of tracer's name.
        """
        return self.sm.inspect_all_tracers()

    def get_all_collector_ids(self) -> List[str]:
        """
        Get all collector id from database.

        Returns:
            List[str]: List of collector id.
        """
        return self.sm.inspect_all_collector_ids()

    def _table_brief(
        self,
        table_name: str,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> Brief:
        """
        Get a brief of a table.

        Args:
            table_name (str): Table's name.

        Returns:
            Brief: A brief of this table.
        """
        tracer = self.sm.table_name_to_tracer(table_name)
        collector_id = self.sm.table_name_to_collector_id(table_name)
        m = self.sm.get_tracking_model(tracer, collector_id)

        start_statm = select(m).order_by(m.dt.asc())
        end_statm = select(m).order_by(m.dt.desc())
        count_statm = select(func.count()).select_from(m)
        if start_datetime:
            start_statm = start_statm.where(m.dt >= start_datetime)
            count_statm = count_statm.where(m.dt >= start_datetime)
        if end_datetime:
            end_statm = end_statm.where(m.dt <= end_datetime)
            count_statm = count_statm.where(m.dt <= end_datetime)

        with self.sm.begin() as session:
            return Brief(
                tracer=tracer,
                collector_id=collector_id,
                start=session.execute(start_statm).first()[0].dt,
                end=session.execute(end_statm).first()[0].dt,
                count=session.execute(count_statm).scalar(),
                fields=m.inspect_fields(),
            )

    def brief(
        self,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> AnalyzerBrief:
        """
        Get a brief of this analyzer.

        Returns:
            AnalyzerBrief: A brief of this analyzer.
        """
        briefs = [
            self._table_brief(t, start_datetime, end_datetime) for t in self.sm.inspect_all_tables()
        ]

        return AnalyzerBrief(
            tracers=[brief.tracer for brief in briefs],
            collector_ids=[brief.collector_id for brief in briefs],
            briefs=briefs,
        )
