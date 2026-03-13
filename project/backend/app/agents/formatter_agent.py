from __future__ import annotations

from typing import Any

from app.schemas.chart_schema import ChartSpec
from app.schemas.report_schema import ReportSpec
from app.schemas.response_schema import APIResponse
from app.schemas.table_schema import TableSpec


class FormatterAgent:
    """Format pipeline outputs into a frontend-safe structured API response."""

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        report = self._parse_report(payload.get("report") or payload.get("report_output"))
        charts = self._parse_charts(payload.get("charts") or payload.get("chart_output") or [])
        tables = self._parse_tables(payload.get("tables") or payload.get("table_output") or [])
        sources = self._parse_sources(payload.get("sources") or [])

        content = self._build_content(
            report=report,
            chart_count=len(charts),
            table_count=len(tables),
            source_count=len(sources),
        )

        response = APIResponse(
            content=content,
            report=report,
            charts=charts,
            tables=tables,
            sources=sources,
        )
        return response.model_dump()

    @staticmethod
    def _build_content(
        report: ReportSpec | None,
        chart_count: int,
        table_count: int,
        source_count: int,
    ) -> str:
        if report is not None:
            return (
                "Your report is ready. "
                f"Included {chart_count} chart(s), {table_count} table(s), and {source_count} source reference(s)."
            )
        return (
            "Processed your request. "
            f"Included {chart_count} chart(s), {table_count} table(s), and {source_count} source reference(s)."
        )

    @staticmethod
    def _parse_report(raw: Any) -> ReportSpec | None:
        if raw is None:
            return None
        if isinstance(raw, ReportSpec):
            return raw
        if isinstance(raw, dict):
            return ReportSpec(**raw)
        return None

    @staticmethod
    def _parse_charts(raw_charts: list[Any]) -> list[ChartSpec]:
        charts: list[ChartSpec] = []
        for item in raw_charts:
            if isinstance(item, ChartSpec):
                charts.append(item)
            elif isinstance(item, dict):
                charts.append(ChartSpec(**item))
        return charts

    @staticmethod
    def _parse_tables(raw_tables: list[Any]) -> list[TableSpec]:
        tables: list[TableSpec] = []
        for item in raw_tables:
            if isinstance(item, TableSpec):
                tables.append(item)
            elif isinstance(item, dict):
                tables.append(TableSpec(**item))
        return tables

    @staticmethod
    def _parse_sources(raw_sources: list[Any]) -> list[str]:
        return [str(source) for source in raw_sources if str(source).strip()]
