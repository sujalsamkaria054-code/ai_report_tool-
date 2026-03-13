from __future__ import annotations

from typing import Any

from app.schemas.chart_schema import ChartSpec
from app.services.chart_service import ChartService


class ChartAgent:
    def __init__(self, chart_service: ChartService | None = None) -> None:
        self.chart_service = chart_service or ChartService()

    def run(self, payload: dict[str, Any]) -> list[ChartSpec]:
        if not payload or payload.get("status") == "no_data":
            return []
        return self.chart_service.generate_charts(payload)
