from __future__ import annotations

from typing import Any

import pandas as pd

from app.schemas.table_schema import TableSpec
from app.services.dataframe_service import DataFrameService


class AnalysisAgent:
    def __init__(self, dataframe_service: DataFrameService | None = None) -> None:
        self.dataframe_service = dataframe_service or DataFrameService()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        tables = self._extract_tables(payload)
        if not tables:
            return {
                "status": "no_data",
                "message": "No table data available for analysis.",
                "analysis": [],
            }

        frames = self.dataframe_service.from_table_specs(tables)
        analysis = [self._analyze_table(name, frame) for name, frame in frames.items()]

        return {
            "status": "ok",
            "message": "Analysis completed.",
            "analysis": analysis,
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

    def _analyze_table(self, name: str, frame: pd.DataFrame) -> dict[str, Any]:
        numeric_cols = self.dataframe_service.numeric_columns(frame)

        return {
            "table_name": name,
            "row_count": int(len(frame)),
            "column_count": int(len(frame.columns)),
            "numeric_columns": numeric_cols,
            "summary_stats": self._summary_stats(frame, numeric_cols),
            "grouped_aggregations": self._grouped_aggregations(frame, numeric_cols),
            "top_bottom_values": self._top_bottom_values(frame, numeric_cols),
            "trend_detection": self._trend_detection(frame, numeric_cols),
        }

    def _summary_stats(self, frame: pd.DataFrame, numeric_cols: list[str]) -> dict[str, dict[str, float | int | None]]:
        result: dict[str, dict[str, float | int | None]] = {}
        for col in numeric_cols:
            series = frame[col].dropna()
            result[col] = {
                "count": int(series.count()),
                "mean": float(series.mean()) if not series.empty else None,
                "min": float(series.min()) if not series.empty else None,
                "max": float(series.max()) if not series.empty else None,
                "sum": float(series.sum()) if not series.empty else None,
            }
        return result

    def _grouped_aggregations(self, frame: pd.DataFrame, numeric_cols: list[str]) -> dict[str, Any]:
        if not numeric_cols or frame.empty:
            return {}

        group_col = self.dataframe_service.first_categorical_column(frame, excluded=set(numeric_cols))
        if group_col is None:
            return {}

        grouped = frame.groupby(group_col, dropna=False)[numeric_cols].agg(["sum", "mean", "count"])
        grouped.columns = [f"{metric}_{agg}" for metric, agg in grouped.columns]
        grouped = grouped.reset_index()
        return {
            "group_by": group_col,
            "rows": self.dataframe_service.to_records(grouped),
        }

    def _top_bottom_values(self, frame: pd.DataFrame, numeric_cols: list[str], n: int = 3) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for col in numeric_cols:
            series = frame[col]
            if series.dropna().empty:
                result[col] = {"top": [], "bottom": []}
                continue

            top = frame.nlargest(min(n, len(frame)), col)
            bottom = frame.nsmallest(min(n, len(frame)), col)
            result[col] = {
                "top": self._value_rows(top, col),
                "bottom": self._value_rows(bottom, col),
            }
        return result

    def _trend_detection(self, frame: pd.DataFrame, numeric_cols: list[str]) -> dict[str, str]:
        trends: dict[str, str] = {}
        for col in numeric_cols:
            series = frame[col].dropna().reset_index(drop=True)
            if len(series) < 2:
                trends[col] = "insufficient_data"
                continue

            first = float(series.iloc[0])
            last = float(series.iloc[-1])
            if last > first:
                trends[col] = "increasing"
            elif last < first:
                trends[col] = "decreasing"
            else:
                trends[col] = "flat"
        return trends

    @staticmethod
    def _value_rows(frame: pd.DataFrame, value_column: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for idx, row in frame.iterrows():
            rows.append({"row_index": int(idx), "value": row[value_column]})
        return rows
