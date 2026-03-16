import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.chart_schema import ChartSpec
from app.schemas.report_schema import ReportSpec
from app.schemas.table_schema import TableSpec


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = ""
    report: ReportSpec | None = None
    charts: list[ChartSpec] = Field(default_factory=list)
    tables: list[TableSpec] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    document_id: str | None = None

    @field_validator("content")
    @classmethod
    def validate_content_is_human_readable(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return value

        if len(stripped) > 600:
            raise ValueError("Content summary is too long for frontend-safe rendering.")

        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                stripped = "\n".join(lines[1:-1]).strip()

        try:
            parsed: Any = json.loads(stripped)
        except json.JSONDecodeError:
            return value

        if isinstance(parsed, dict) and any(
            key in parsed for key in ("chart", "charts", "chart_type", "series", "x", "y", "labels", "rows")
        ):
            raise ValueError("Structured payloads must not be embedded in content.")

        if isinstance(parsed, list):
            raise ValueError("Array-like payloads must not be embedded in content.")

        return value

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, value: list[str]) -> list[str]:
        compressed_pattern = re.compile(r"^[A-Za-z0-9+/=]{180,}$")
        safe: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                continue
            if len(text) > 600:
                continue
            if compressed_pattern.match(text):
                continue
            safe.append(text)
        return safe[:20]
