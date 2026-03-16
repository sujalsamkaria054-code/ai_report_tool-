from __future__ import annotations

from typing import Any

from app.schemas.report_schema import ReportSpec
from app.services.report_service import ReportService


class ReportAgent:
    """Narrative report generator that consumes upstream outputs only."""

    def __init__(self, report_service: ReportService | None = None) -> None:
        self.report_service = report_service or ReportService()

    def run(self, payload: dict[str, Any]) -> ReportSpec:
        return self.report_service.build(payload)
