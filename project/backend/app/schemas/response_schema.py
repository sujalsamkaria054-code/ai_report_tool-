import json
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.chart_schema import ChartSpec
from app.schemas.report_schema import ReportSpec
from app.schemas.table_schema import TableSpec


class APIResponse(BaseModel):
    content: str = ""
    report: ReportSpec | None = None
    charts: list[ChartSpec] = Field(default_factory=list)
    tables: list[TableSpec] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)

    @field_validator("content")
    @classmethod
    def prevent_raw_chart_json_in_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return value

        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                stripped = "\n".join(lines[1:-1]).strip()

        try:
            parsed: Any = json.loads(stripped)
        except json.JSONDecodeError:
            return value

        if isinstance(parsed, dict) and any(
            key in parsed for key in ("chart", "charts", "chart_type", "series", "x", "y", "labels")
        ):
            raise ValueError(
                "Chart JSON must not be embedded in content. Use the dedicated 'charts' field instead."
            )

        if isinstance(parsed, list) and parsed and all(isinstance(item, dict) for item in parsed):
            chart_keys = {"chart", "charts", "chart_type", "series", "x", "y", "labels"}
            if any(chart_keys.intersection(item.keys()) for item in parsed):
                raise ValueError(
                    "Chart JSON must not be embedded in content. Use the dedicated 'charts' field instead."
                )

        return value
