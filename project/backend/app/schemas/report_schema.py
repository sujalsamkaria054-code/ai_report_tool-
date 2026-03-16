from pydantic import BaseModel, ConfigDict, Field


class ReportSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str = ""
    insights: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    conclusion: str = ""
