from __future__ import annotations

from typing import Any

from app.schemas.chart_schema import ChartSpec
from app.services.chart_service import ChartService


class ChartAgent:
    def __init__(self, chart_service: ChartService | None = None) -> None:
        self.chart_service = chart_service or ChartService()

    def run(self, payload: dict[str, Any]) -> list[ChartSpec]:
        if not payload:
            return []

        analysis = payload.get("analysis", {}) if isinstance(payload, dict) else {}
        tables = payload.get("tables", []) if isinstance(payload, dict) else []

        if not isinstance(analysis, dict) or analysis.get("status") == "no_data":
            return []
        if not isinstance(tables, list) or not tables:
            return []

        return self.chart_service.generate_charts(payload)
