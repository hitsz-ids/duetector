from __future__ import annotations

from datetime import datetime
from typing import Any

from duetector.analyzer.models import AnalyzerBrief, Tracking
from duetector.config import Configuable


class Analyzer(Configuable):
    """
    A base class for all analyzers.
    """

    default_config = {
        "disabled": False,
    }
    """
    Default config for ``Analyzer``.
    """

    @property
    def disabled(self) -> bool:
        """
        Weather this analyzer is disabled.
        """
        return self.config.disabled

    @property
    def config_scope(self):
        """
        Config scope for this analyzer.

        Subclasses cloud override this.
        """
        return self.__class__.__name__.lower()

    def get_all_tracers(self) -> list[str]:
        """
        Get all tracers from storage.

        Returns:
            List[str]: List of tracer's name.
        """
        raise NotImplementedError

    def get_all_collector_ids(self) -> list[str]:
        """
        Get all collector id from storage.

        Returns:
            List[str]: List of collector id.
        """
        raise NotImplementedError

    async def query(
        self,
        tracers: list[str] | None = None,
        collector_ids: list[str] | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        start: int = 0,
        limit: int = 20,
        columns: list[str] | None = None,
        where: dict[str, Any] | None = None,
        distinct: bool = False,
        order_by_asc: list[str] | None = None,
        order_by_desc: list[str] | None = None,
    ) -> list[Tracking]:
        """
        Query all tracking records from backend.

        Note:
            Some storage implementations do not guarantee the correct implementation of all parameters.
            Some parameters may be ignored.

        Args:
            tracers (Optional[List[str]], optional): Tracer's name. Defaults to None, all tracers will be queried.
            collector_ids (Optional[List[str]], optional): Collector id. Defaults to None, all collector id will be queried.
            start_datetime (Optional[datetime], optional): Start time. Defaults to None.
            end_datetime (Optional[datetime], optional): End time. Defaults to None.
            start (int, optional): Start index. Defaults to 0.
            limit (int, optional): Limit of records, depends on backend implementations. Defaults to 20. ``0`` means no limit.
            columns (Optional[List[str]], optional): Columns to query. Defaults to None, all columns will be queried.
            where (Optional[Dict[str, Any]], optional): Where clause. Defaults to None.
            distinct (bool, optional): Distinct. Defaults to False.
            order_by_asc (Optional[List[str]], optional): Order by asc. Defaults to None.
            order_by_desc (Optional[List[str]], optional): Order by desc. Defaults to None.
        Returns:
            List[duetector.analyzer.models.Tracking]: List of tracking records.
        """
        raise NotImplementedError

    async def brief(
        self,
        tracers: list[str] | None = None,
        collector_ids: list[str] | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
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
            inspect_type (bool, optional): Weather fileds's value is type or type name. Defaults to False, type name.

        Returns:
            AnalyzerBrief: A brief of this analyzer.
        """
        raise NotImplementedError

    async def analyze(self):
        # TODO: Not design yet.
        pass
