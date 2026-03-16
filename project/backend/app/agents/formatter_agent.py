from __future__ import annotations

import re
from typing import Any

from app.schemas.chart_schema import ChartSpec
from app.schemas.report_schema import ReportSpec
from app.schemas.response_schema import APIResponse
from app.schemas.table_schema import TableSpec
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FormatterAgent:
    """Format pipeline outputs into a frontend-safe structured API response."""

    _MAX_TEXT_LEN = 2000
    _COMPRESSED_PATTERN = re.compile(r"^[A-Za-z0-9+/=]{180,}$")

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
        logger.info(
            "Formatter output summary | has_report=%s charts=%d tables=%d sources=%d",
            bool(report),
            len(charts),
            len(tables),
            len(sources),
        )
        return response.model_dump()

    @staticmethod
    def _build_content(
        report: ReportSpec | None,
        chart_count: int,
        table_count: int,
        source_count: int,
    ) -> str:
        prefix = "Your report is ready." if report is not None else "Processed your request."
        return (
            f"{prefix} Included {chart_count} chart(s), "
            f"{table_count} table(s), and {source_count} source reference(s)."
        )

    def _parse_report(self, raw: Any) -> ReportSpec | None:
        if raw is None:
            return None
        if isinstance(raw, ReportSpec):
            return raw
        if isinstance(raw, dict):
            try:
                return ReportSpec(**raw)
            except Exception:
                logger.warning("Dropping malformed report payload.")
                return None
        logger.warning("Dropping non-dict report payload of type %s.", type(raw).__name__)
        return None

    def _parse_charts(self, raw_charts: list[Any]) -> list[ChartSpec]:
        charts: list[ChartSpec] = []
        for item in raw_charts:
            try:
                if isinstance(item, ChartSpec):
                    charts.append(item)
                elif isinstance(item, dict):
                    charts.append(ChartSpec(**item))
                else:
                    logger.warning("Dropping non-dict chart payload of type %s.", type(item).__name__)
            except Exception:
                logger.warning("Dropping malformed chart payload.")
        return charts

    def _parse_tables(self, raw_tables: list[Any]) -> list[TableSpec]:
        tables: list[TableSpec] = []
        for item in raw_tables:
            if not isinstance(item, (dict, TableSpec)):
                logger.warning("Dropping non-dict table payload of type %s.", type(item).__name__)
                continue

            candidate = item.model_dump() if isinstance(item, TableSpec) else item
            if not self._is_safe_table(candidate):
                logger.warning("Dropping unsafe or malformed table payload.")
                continue

            try:
                tables.append(TableSpec(**candidate))
            except Exception:
                logger.warning("Dropping table payload that failed schema validation.")

        return tables

    def _parse_sources(self, raw_sources: list[Any]) -> list[str]:
        clean_sources: list[str] = []
        for source in raw_sources:
            if isinstance(source, bytes):
                logger.warning("Dropping bytes source payload.")
                continue

            value = str(source).strip()
            if not value:
                continue
            if self._looks_unsafe_text(value):
                logger.warning("Dropping unsafe source payload.")
                continue
            clean_sources.append(value)
        return clean_sources[:20]

    def _is_safe_table(self, candidate: dict[str, Any]) -> bool:
        name = candidate.get("name")
        columns = candidate.get("columns")
        rows = candidate.get("rows")

        if not isinstance(name, str) or not name.strip():
            return False
        if not isinstance(columns, list) or not all(isinstance(col, str) and col.strip() for col in columns):
            return False
        if not isinstance(rows, list):
            return False

        for row in rows:
            if not isinstance(row, dict):
                return False
            for key, value in row.items():
                if not isinstance(key, str):
                    return False
                if isinstance(value, bytes):
                    return False
                if isinstance(value, (dict, list, set, tuple)):
                    # Nested parser/raw objects are not frontend-safe table cells.
                    return False
                if isinstance(value, str) and self._looks_unsafe_text(value):
                    return False

        return True

    def _looks_unsafe_text(self, value: str) -> bool:
        text = value.strip()
        if not text:
            return False
        if len(text) > self._MAX_TEXT_LEN:
            return True
        if self._COMPRESSED_PATTERN.match(text):
            return True
        return False
