from __future__ import annotations

from typing import Optional

from duetector.collectors.models import Tracking as CTracking


class OTelInspector:
    service_prefix = "duetector"
    service_sep = "-"

    @classmethod
    def generate_service_name(cls, identifier: str) -> str:
        return cls.service_sep.join([f"{cls.service_prefix}", f"{identifier}"])

    @classmethod
    def get_identifier(cls, service_name: str) -> Optional[str]:
        if not service_name.startswith(cls.service_prefix):
            return None

        return service_name.replace(cls.service_prefix + cls.service_sep, "")

    @classmethod
    def generate_span_name(cls, t: CTracking | str) -> str:
        if isinstance(t, str):
            return t
        return t.tracer

    @classmethod
    def get_tracer_name(cls, span_name: str) -> str:
        return span_name
