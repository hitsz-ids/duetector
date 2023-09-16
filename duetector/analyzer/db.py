from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select

from duetector.analyzer.base import Analyzer
from duetector.analyzer.models import AnalyzerBrief, Brief, Tracking
from duetector.db import SessionManager
from duetector.extension.analyzer import hookimpl
from duetector.log import logger


class DBAnalyzer(Analyzer):
    """
    A analyzer using database.

    We design this analyzer to be a top module, so it can be used as a standalone tools.

    In this analyzer, we use ``SessionManager`` to manage database session.

    Config scope is ``db_analyzer``. ``db_analyzer.db`` is the scope for ``SessionManager``.

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

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel
        self.sm: SessionManager = SessionManager(self.config._config_dict)

    def query(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
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
            tracers (Optional[List[str]], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_ids (Optional[List[str]], optional): Collector id. Defaults to None, all collector id will be queried.
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
        if tracers:
            tables = [t for t in tables if self.sm.table_name_to_tracer(t) in tracers]
        if collector_ids:
            tables = [t for t in tables if self.sm.table_name_to_collector_id(t) in collector_ids]

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

            logger.debug(f"Querying {tracer}@{collector_id} with statm: {statm}")
            with self.sm.begin() as session:
                r.extend(
                    [
                        self._convert_row_to_tracking(columns, r, tracer)
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
        inspect: bool = True,
        inspect_type: bool = False,
        distinct: bool = False,
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

        if not inspect:
            logger.debug(f"Briefing {tracer}@{collector_id} without inspect")
            return Brief(
                tracer=tracer,
                collector_id=collector_id,
                fields=m.inspect_fields(value_as_type=inspect_type),
            )
        columns = m.inspect_fields().keys()
        statm = select(*[getattr(m, k) for k in columns])
        if distinct:
            statm = statm.distinct()
        if start_datetime:
            statm = statm.where(m.dt >= start_datetime)
        if end_datetime:
            statm = statm.where(m.dt <= end_datetime)

        start_statm = statm.order_by(m.dt.asc())
        end_statm = statm.order_by(m.dt.desc())
        count_statm = select(func.count()).select_from(statm.subquery())
        logger.debug(f"Briefing {tracer}@{collector_id} with statm: {start_statm}")
        with self.sm.begin() as session:
            start_tracking = self._convert_row_to_tracking(
                columns, session.execute(start_statm).first(), tracer
            )
            end_tracking = self._convert_row_to_tracking(
                columns, session.execute(end_statm).first(), tracer
            )

            return Brief(
                tracer=tracer,
                collector_id=collector_id,
                start=start_tracking.dt,
                end=end_tracking.dt,
                count=session.execute(count_statm).scalar(),
                fields=m.inspect_fields(value_as_type=inspect_type),
            )

    def _convert_row_to_tracking(self, columns: List[str], row: Any, tracer: str) -> Tracking:
        """
        Convert a row to a tracking record.

        Args:
            columns (List[str]): Columns.
            row (Any): Row.
            tracer (str): Tracer's name.

        Returns:
            duetector.analyzer.models.Tracking: A tracking record.
        """
        if not row:
            return Tracking(tracer=tracer)

        return Tracking(tracer=tracer, **{k: v for k, v in zip(columns, row)})

    def brief(
        self,
        tracers: Optional[List[str]] = None,
        collector_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        with_details: bool = True,
        distinct: bool = False,
        inspect_type: bool = False,
    ) -> AnalyzerBrief:
        """
        Get a brief of this analyzer.

        Args:
            tracers (Optional[List[str]], optional):
                Tracers. Defaults to None, all tracers will be queried.
                If a specific tracer is not found, it will be ignored.
            collector_ids (Optional[List[str]], optional):
                Collector ids. Defaults to None, all collector ids will be queried.
                If a specific collector id is not found, it will be ignored.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            with_details (bool, optional): With details. Defaults to True.
            distinct (bool, optional): Distinct. Defaults to False.

        Returns:
            AnalyzerBrief: A brief of this analyzer.
        """

        tables = self.sm.inspect_all_tables()
        if tracers:
            tables = [t for t in tables if self.sm.table_name_to_tracer(t) in tracers]
        if collector_ids:
            tables = [t for t in tables if self.sm.table_name_to_collector_id(t) in collector_ids]

        briefs: List[Brief] = [
            self._table_brief(
                t,
                start_datetime,
                end_datetime,
                inspect=with_details,
                distinct=distinct,
                inspect_type=inspect_type,
            )
            for t in tables
        ]

        return AnalyzerBrief(
            tracers=set([brief.tracer for brief in briefs]),
            collector_ids=set([brief.collector_id for brief in briefs]),
            briefs={f"{brief.tracer}@{brief.collector_id}": brief for brief in briefs},
        )


@hookimpl
def init_analyzer(config):
    return DBAnalyzer(config)
