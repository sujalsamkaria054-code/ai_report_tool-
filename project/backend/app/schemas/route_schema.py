from typing import Literal

from pydantic import BaseModel, Field


RouteType = Literal["rag_only", "analysis_only", "chart_only", "report_only", "hybrid"]


class RouteRequest(BaseModel):
    query: str = Field(..., min_length=1)


class RouteResponse(BaseModel):
    route: RouteType
    needs_rag: bool
    needs_analysis: bool
    needs_chart: bool
    needs_report: bool
