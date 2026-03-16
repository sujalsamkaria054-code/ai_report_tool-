from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TableSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    numeric_columns: list[str] = Field(default_factory=list)
    preview: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, value: list[str]) -> list[str]:
        return [str(column).strip() for column in value if str(column).strip()]

    @field_validator("rows")
    @classmethod
    def validate_rows(cls, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        safe_rows: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            safe_row: dict[str, Any] = {}
            for key, value in row.items():
                if not isinstance(key, str):
                    continue
                if isinstance(value, bytes):
                    continue
                if isinstance(value, (dict, list, set, tuple)):
                    continue
                safe_row[key] = value
            if safe_row:
                safe_rows.append(safe_row)
        return safe_rows
