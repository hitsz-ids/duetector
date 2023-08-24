from contextlib import contextmanager
from threading import Lock
from typing import Any, Dict, Generator, Optional

import sqlalchemy  # type: ignore
from sqlalchemy.orm import (  # type: ignore
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.types import JSON  # type: ignore

from duetector.collectors.models import Tracking
from duetector.config import Configuable


class TrackingMixin:
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
        return f"<Tracking [{self.pid} {self.comm}] {self.timestamp}>"


class SessionManager(Configuable):
    """
    A wrapper for sqlalchemy session

    Config:
        - table_prefix: str  prefix for all table names
        - engine: Dict[str, Any]  config for sqlalchemy.create_engine

    """

    config_scope = "db"

    default_config = {
        "table_prefix": "duetector_tracking",
        "engine": {
            "url": "sqlite:///",
        },
    }

    def __repr__(self):
        url = self.config.engine.url or ""
        if "@" in url:
            database_type = self.config.engine.url.split(":")[0]
            safe_url = f'{database_type}://********@{(self.config.engine.url or "").split("@")[-1]}'
        else:
            safe_url = url

        return f"<[SessionManager {safe_url}]{self.table_prefix}*>"

    def __init__(self, config: Optional[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self._engine: Optional[sqlalchemy.engine.Engine] = None
        self._sessionmaker: Optional[sessionmaker] = None
        self._tracking_models: Dict[str, type] = {}
        self.mutex = Lock()

    @property
    def debug(self):
        return self.config.debug or self.config.echo

    @property
    def table_prefix(self):
        return self.config.table_prefix

    @property
    def engine_config(self) -> Dict[str, Any]:
        config = self.config.engine.config_dict
        if self.debug:
            config["echo"] = True
        return config

    @property
    def engine(self):
        if not self._engine:
            self._engine = sqlalchemy.create_engine(**self.engine_config)
        return self._engine

    @property
    def sessionmaker(self):
        if not self._sessionmaker:
            self._sessionmaker = sessionmaker(bind=self.engine)
        return self._sessionmaker

    @contextmanager
    def begin(self) -> Generator[Session, None, None]:
        with self.sessionmaker.begin() as session:
            yield session

    def get_tracking_model(self, tracer: str = "unknown", collector_id: str = "") -> type:
        # For thread safety
        with self.mutex:
            if tracer in self._tracking_models:
                return self._tracking_models[tracer]

            class Base(DeclarativeBase):
                pass

            class TrackingModel(Base, TrackingMixin):
                __tablename__ = f"{self.table_prefix}:{tracer}@{collector_id}"

                def to_tracking(self) -> Tracking:
                    return Tracking(
                        tracer=tracer,
                        pid=self.pid,
                        uid=self.uid,
                        gid=self.gid,
                        timestamp=self.timestamp,
                        comm=self.comm,
                        cwd=self.cwd,
                        fname=self.fname,
                        extended=self.extended,
                    )

            try:
                self._tracking_models[tracer] = self._init_tracking_model(TrackingModel)
            except Exception as e:
                # FIXME: unregister TrackingModel
                raise
            return self._tracking_models[tracer]

    def get_all_model(self) -> Dict[str, type]:
        return self._tracking_models.copy()

    def _init_tracking_model(self, tracking_model: type) -> type:
        if not sqlalchemy.inspect(self.engine).has_table(tracking_model.__tablename__):
            tracking_model.__table__.create(self.engine)
        return tracking_model


if __name__ == "__main__":
    print(SessionManager())
