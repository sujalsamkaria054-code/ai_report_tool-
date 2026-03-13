from pydantic import BaseModel, Field


class ReportSpec(BaseModel):
    title: str
    summary: str = ""
    insights: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    conclusion: str = ""
