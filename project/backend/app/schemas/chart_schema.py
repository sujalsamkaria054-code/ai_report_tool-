from typing import Any, Literal

from pydantic import BaseModel, Field


ChartType = Literal["bar", "line", "pie"]


class ChartSeries(BaseModel):
    name: str
    values: list[float | int] = Field(default_factory=list)


class ChartSpec(BaseModel):
    chart_type: ChartType
    title: str = ""
    x_axis: list[str] = Field(default_factory=list)
    series: list[ChartSeries] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    values: list[float | int] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
