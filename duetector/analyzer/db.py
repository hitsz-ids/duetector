from typing import Any, Dict, List, Optional

from sqlalchemy import select

from duetector.analyzer.base import Analyzer
from duetector.collectors.db import DBCollector
from duetector.collectors.models import Tracking
from duetector.db import SessionManager


class DBAnalyzer(Analyzer):
    """
    A analyzer using database.

    As a top model, it will init a ``SessionManager`` and pass it to submodels.

    Config scope is ``db_analyzer``.

    Example:

        .. code-block:: python

            from duetector.analyzer.db import DBAnalyzer
            from duetector.collectors.models import Tracking

            collector_id = "db_analyzer_tests_collector"
            tracking = Tracking(
                tracer="t",
            )
            db_analyzer = DBAnalyzer()
            m = db_analyzer.sm.get_tracking_model(tracking.tracer, collector_id)
            with db_analyzer.sm.begin() as session:
                session.add(m(**tracking.model_dump(exclude=["tracer"])))
                session.commit()

            assert tracking in db_analyzer.query_all()
            assert tracking in db_analyzer.query_all(tracer=tracking.tracer)
            assert tracking in db_analyzer.query_all(collector_id=collector_id)
            assert tracking in db_analyzer.query_all(
                    tracer=tracking.tracer, collector_id=collector_id
            )
            assert not db_analyzer.query_all(tracer="not-exist")
            assert not db_analyzer.query_all(collector_id="not-exist")

    Note:
        Currently, it will **NOT** be configured by ``DBcollector``'s config,
        as we design it to be a standalone model.
    """

    default_config = {
        **Analyzer.default_config,
        "db": {
            **DBCollector.default_config.get("db", {})
        },  # Use the same default config as DBCollector
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

    def query_all(
        self,
        tracer: Optional[str] = None,
        collector_id: Optional[str] = None,
    ) -> List[Tracking]:
        """
        Query all tracking records from database.

        Args:
            tracer (Optional[str], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_id (Optional[str], optional): Collector id. Defaults to None, all collector id will be queried.

        Returns:
            List[Tracking]: List of tracking records.

        TODO:
            Time range support. Depends on tracer's implementation.
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
            with self.sm.begin() as session:
                r.extend([t.to_tracking() for t, *_ in session.execute(select(m)).fetchall()])
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
