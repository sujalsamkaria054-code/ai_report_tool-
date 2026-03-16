from dataclasses import dataclass, field

from app.schemas.route_schema import RouteType


@dataclass(frozen=True)
class GraphRoutes:
    """Base route-to-node transitions for LangGraph-style orchestration.

    Note: `report_only` can be enriched at runtime in `OrchestrationGraph._resolve_path`
    when normalized tables are present, so reports can include structured analysis.
    """

    route_map: dict[RouteType, list[str]] = field(
        default_factory=lambda: {
            "rag_only": ["rag", "formatter"],
            "analysis_only": ["analysis", "formatter"],
            "chart_only": ["analysis", "chart", "formatter"],
            "report_only": ["rag", "report", "formatter"],
            "hybrid": ["rag", "analysis", "chart", "report", "formatter"],
        }
    )

    def get_path(self, route: RouteType) -> list[str]:
        return self.route_map[route]
