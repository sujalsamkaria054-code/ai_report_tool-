from __future__ import annotations

from typing import Any

import pandas as pd

from app.schemas.table_schema import TableSpec


class DataFrameService:
    """Helpers to normalize extracted tables into pandas DataFrames."""

    def from_table_specs(self, tables: list[TableSpec]) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        for index, table in enumerate(tables, start=1):
            name = table.name or f"table_{index}"
            rows = table.rows or []

            if rows:
                frame = pd.DataFrame(rows)
            else:
                frame = pd.DataFrame(columns=table.columns)

            frames[name] = frame
        return frames

    @staticmethod
    def numeric_columns(frame: pd.DataFrame) -> list[str]:
        numeric_frame = frame.select_dtypes(include="number")
        return [str(column) for column in numeric_frame.columns]

    @staticmethod
    def first_categorical_column(frame: pd.DataFrame, excluded: set[str]) -> str | None:
        for column in frame.columns:
            name = str(column)
            if name not in excluded:
                return name
        return None

    @staticmethod
    def to_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
        return frame.where(frame.notna(), None).to_dict(orient="records")
