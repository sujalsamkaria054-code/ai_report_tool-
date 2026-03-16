from typing import Any

from pydantic import BaseModel, Field


class TableSpec(BaseModel):
    name: str = ""
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    numeric_columns: list[str] = Field(default_factory=list)
    preview: list[dict[str, Any]] = Field(default_factory=list)
