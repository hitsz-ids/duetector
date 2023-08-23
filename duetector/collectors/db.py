from typing import Any, Dict, Optional

from sqlalchemy import select

from duetector.collectors.base import Collector
from duetector.collectors.models import Tracking
from duetector.db import SessionManager
from duetector.extension.collector import hookimpl


class DBCollector(Collector):
    default_config = {
        **Collector.default_config,
        "db": {
            **SessionManager.default_config,
            "engine": {
                "url": "sqlite:///duetector-dbcollector.sqlite3",
            },
        },
    }

    # TODO: A better repr not present sensitive info
    def __repr__(self):
        return f"<DBCollector @{self.id}>"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        # Init as a submodel
        self.sm = SessionManager(self.config.config_dict)

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
                    "count": len(session.execute(select(m)).fetchall()),
                    "first at": session.execute(select(m)).first()[0].timestamp,
                    "last": session.execute(select(m).order_by(m.id.desc()))
                    .first()[0]
                    .to_tracking(),
                }
                for tracer, m in self.sm.get_all_model()
            }


@hookimpl
def init_collector(config):
    return DBCollector(config)
