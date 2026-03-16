from typing import Any

from pydantic import BaseModel, Field

from app.schemas.chart_schema import ChartSpec
from app.schemas.report_schema import ReportSpec
from app.schemas.route_schema import RouteType
from app.schemas.table_schema import TableSpec


class GraphState(BaseModel):
    user_query: str = ""
    document_id: str | None = None
    route: RouteType | None = None

    router_output: dict = Field(default_factory=dict)
    rag_output: str = ""
    analysis_output: dict = Field(default_factory=dict)
    chart_output: list[ChartSpec] = Field(default_factory=list)
    report_output: ReportSpec | None = None
    formatter_output: dict[str, Any] = Field(default_factory=dict)

    tables: list[TableSpec] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
