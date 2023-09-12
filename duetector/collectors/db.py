import copy
from typing import Any, Dict, Optional

from sqlalchemy import func, select  # type: ignore

from duetector.collectors.base import Collector
from duetector.collectors.models import Tracking
from duetector.db import SessionManager
from duetector.extension.collector import hookimpl


class DBCollector(Collector):
    """
    A collector using database, sqlite by default.

    Every tracker will create a table in database, see ``SessionManager``.get_tracking_model

    Config:
        - ``db``: A ``SessionManager`` config
    """

    default_config = {
        **Collector.default_config,
        "db": {
            **SessionManager.default_config,
            "engine": {
                "url": "sqlite:///duetector-dbcollector.sqlite3",
            },
        },
    }

    def __repr__(self):
        config_without_db = copy.deepcopy(self.config._config_dict)
        config_without_db.pop("db", None)
        return f"<[DBCollector {self.sm}] {config_without_db}>"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel
        self.sm = SessionManager(self.config._config_dict)

    def _emit(self, t: Tracking):
        m = self.sm.get_tracking_model(t.tracer, self.id)
        with self.sm.begin() as session:
            tracking = m(**t.model_dump(exclude=["tracer"]))
            session.add(tracking)
            session.commit()

    def summary(self) -> Dict:
        with self.sm.begin() as session:
            return {
                tracer: {
                    "count": session.execute(select(func.count()).select_from(m)).scalar(),
                    "first at": session.execute(select(m)).first()[0].dt,
                    "last": session.execute(select(m).order_by(m.id.desc()))  # type: ignore
                    .first()[0]
                    .to_collector_tracking(),
                }
                for tracer, m in self.sm.get_all_models().items()
            }


@hookimpl
def init_collector(config):
    return DBCollector(config)


if __name__ == "__main__":
    print(DBCollector())
