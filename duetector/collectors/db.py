from typing import Any, Dict, Optional

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON

from duetector.utils import Singleton


class Base(DeclarativeBase):
    pass


class TrackingMixix:
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    pid: Mapped[Optional[int]]
    uid: Mapped[Optional[int]]
    gid: Mapped[Optional[int]]
    timestamp: Mapped[Optional[int]]

    comm: Mapped[Optional[str]]
    cwd: Mapped[Optional[str]]
    fname: Mapped[Optional[str]]

    extended: Mapped[Dict[str, Any]] = mapped_column(type_=JSON, default={})

    def __repr__(self):
        return f"<Tracking {self.id}>"


class SessionManager(metaclass=Singleton):
    def __init__(self, config=None):
        # TODO:
        self.config = config
        self._engine: Optional[sqlalchemy.engine.Engine] = None
        self._tracking_models: Dict[str, type] = {}

    @property
    def engine(self):
        if not self._engine:
            self._engine = sqlalchemy.create_engine(
                "sqlite://",
                echo=True
                # self.config.db_url,
                # echo=self.config.debug,
            )
        return self._engine

    def get_tracking_model(self, tracer: str = "unknown") -> type:
        # FIXME: Mutex for thread safety
        if tracer in self._tracking_models:
            return self._tracking_models[tracer]

        class TrackingModel(Base, TrackingMixix):
            __tablename__ = f"duetector_tracking_{tracer}"

        try:
            self._tracking_models[tracer] = self._init_tracking_model(TrackingModel)
        except Exception as e:
            # FIXME: unregister TrackingModel
            raise
        return self._tracking_models[tracer]

    def _init_tracking_model(self, tracking_model: type) -> type:
        if not sqlalchemy.inspect(self.engine).has_table(tracking_model.__tablename__):
            tracking_model.__table__.create(self.engine)
        return tracking_model


if __name__ == "__main__":
    sm = SessionManager()
    m = sm.get_tracking_model()
    print(m())
