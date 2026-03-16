from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.schemas.table_schema import TableSpec
from app.services.dataframe_service import DataFrameService


class AnalysisAgent:
    """Builds a deterministic summary from normalized table specs."""

    def __init__(self, dataframe_service: DataFrameService | None = None) -> None:
        self.dataframe_service = dataframe_service or DataFrameService()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        tables = self._extract_tables(payload)
        if not tables:
            return {
                "status": "no_data",
                "message": "No table data available for analysis.",
                "summary": self._empty_summary(warnings=["No tables were provided."]),
            }

        table_summaries: list[dict[str, Any]] = []
        numeric_fields: set[str] = set()
        date_fields: set[str] = set()
        category_fields: set[str] = set()
        warnings: list[str] = []

        for index, table in enumerate(tables, start=1):
            table_name = table.name or f"table_{index}"
            columns = table.columns or self._discover_columns(table.rows)
            rows = table.rows or table.preview or []
            readable = bool(columns)

            if not readable:
                warnings.append(f"Table '{table_name}' has no readable columns.")
                table_summaries.append(
                    {
                        "table_name": table_name,
                        "row_count": int(table.row_count or len(rows)),
                        "column_count": 0,
                        "readable": False,
                    }
                )
                continue

            table_numeric = self._numeric_fields(table, rows, columns)
            table_dates = self._date_fields(rows, columns)
            table_categories = [
                column for column in columns if column not in table_numeric and column not in table_dates
            ]

            numeric_fields.update(table_numeric)
            date_fields.update(table_dates)
            category_fields.update(table_categories)

            table_summaries.append(
                {
                    "table_name": table_name,
                    "row_count": int(table.row_count or len(rows)),
                    "column_count": int(len(columns)),
                    "readable": True,
                }
            )

        key_metrics = [{"field": metric, "aggregation": "sum"} for metric in sorted(numeric_fields)]
        chart_candidates = self._chart_candidates(
            numeric_fields=sorted(numeric_fields),
            date_fields=sorted(date_fields),
            category_fields=sorted(category_fields),
        )

        if not numeric_fields:
            warnings.append("No numeric fields detected; metric summarization is limited.")
        if not chart_candidates:
            warnings.append("No chart-safe aggregation candidates were detected.")

        summary = {
            "table_count": len(tables),
            "readable_table_count": sum(1 for item in table_summaries if item["readable"]),
            "numeric_field_count": len(numeric_fields),
            "numeric_fields": sorted(numeric_fields),
            "date_fields": sorted(date_fields),
            "category_fields": sorted(category_fields),
            "key_metrics": key_metrics,
            "chart_candidates": chart_candidates,
            "warnings": warnings,
            "table_summaries": table_summaries,
        }

        return {
            "status": "ok",
            "message": "Analysis completed.",
            "summary": summary,
        }

    def _extract_tables(self, payload: dict[str, Any]) -> list[TableSpec]:
        raw_tables = payload.get("tables", [])
        tables: list[TableSpec] = []
        for item in raw_tables:
            if isinstance(item, TableSpec):
                tables.append(item)
            elif isinstance(item, dict):
                tables.append(TableSpec(**item))
        return tables

    @staticmethod
    def _empty_summary(warnings: list[str] | None = None) -> dict[str, Any]:
        return {
            "table_count": 0,
            "readable_table_count": 0,
            "numeric_field_count": 0,
            "numeric_fields": [],
            "date_fields": [],
            "category_fields": [],
            "key_metrics": [],
            "chart_candidates": [],
            "warnings": warnings or [],
            "table_summaries": [],
        }

    @staticmethod
    def _discover_columns(rows: Iterable[dict[str, Any]]) -> list[str]:
        for row in rows:
            if isinstance(row, dict):
                return [str(column) for column in row.keys()]
        return []

    @staticmethod
    def _numeric_fields(table: TableSpec, rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
        if table.numeric_columns:
            return [column for column in table.numeric_columns if column in columns]

        detected: list[str] = []
        for column in columns:
            values = [row.get(column) for row in rows if isinstance(row, dict)]
            if AnalysisAgent._is_numeric_series(values):
                detected.append(column)
        return detected

    @staticmethod
    def _is_numeric_series(values: list[Any]) -> bool:
        non_null = [value for value in values if value is not None and str(value).strip() != ""]
        if not non_null:
            return False

        numeric_like = 0
        for value in non_null:
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                numeric_like += 1
                continue
            try:
                float(str(value).replace(",", ""))
                numeric_like += 1
            except (TypeError, ValueError):
                continue

        return numeric_like > 0 and (numeric_like / len(non_null)) >= 0.8

    @staticmethod
    def _date_fields(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
        candidates: list[str] = []
        for column in columns:
            lower_name = column.lower()
            if any(token in lower_name for token in ["date", "time", "month", "year"]):
                candidates.append(column)
                continue

            sample_values = [row.get(column) for row in rows[:5] if isinstance(row, dict)]
            if sample_values and all(AnalysisAgent._looks_like_date(value) for value in sample_values if value is not None):
                candidates.append(column)
        return candidates

    @staticmethod
    def _looks_like_date(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if "-" in value and len(value) >= 8:
            return True
        if "/" in value and len(value) >= 8:
            return True
        return False

    @staticmethod
    def _chart_candidates(
        numeric_fields: list[str], date_fields: list[str], category_fields: list[str]
    ) -> list[dict[str, str]]:
        if not numeric_fields:
            return []

        candidates: list[dict[str, str]] = []
        if date_fields:
            candidates.append(
                {
                    "type": "line",
                    "x": date_fields[0],
                    "y": numeric_fields[0],
                    "reason": "Time-like field with numeric metric.",
                }
            )
        if category_fields:
            candidates.append(
                {
                    "type": "bar",
                    "x": category_fields[0],
                    "y": numeric_fields[0],
                    "reason": "Category field can group numeric metric.",
                }
            )
            candidates.append(
                {
                    "type": "pie",
                    "category": category_fields[0],
                    "value": numeric_fields[0],
                    "reason": "Single metric split across categories.",
                }
            )
        return candidates
