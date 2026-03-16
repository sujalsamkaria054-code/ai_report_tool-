from app.schemas.route_schema import RouteResponse, RouteType


class RouterAgent:
    """Deterministic keyword-based router for early-stage orchestration."""

    RAG_KEYWORDS = ("summary", "summarize", "explain", "document", "docs")
    ANALYSIS_KEYWORDS = ("compare", "stats", "statistics", "trend", "highest", "lowest")
    CHART_KEYWORDS = ("chart", "graph", "plot", "visualize", "visualise")
    REPORT_KEYWORDS = ("report",)
    HYBRID_HINTS = (
        "detailed analysis",
        "analysis with chart",
        "analysis with charts",
        "report with chart",
        "report with charts",
    )

    def run(self, query: str) -> RouteResponse:
        route = self._classify(query)
        return self._build_response(route)

    def _classify(self, query: str) -> RouteType:
        q = query.lower()

        has_report = self._contains_any(q, self.REPORT_KEYWORDS)
        has_chart = self._contains_any(q, self.CHART_KEYWORDS)
        has_analysis = self._contains_any(q, self.ANALYSIS_KEYWORDS)
        has_hybrid_hint = self._contains_any(q, self.HYBRID_HINTS)

        # 1) report with charts / detailed analysis -> hybrid
        if has_report and (has_chart or has_analysis or has_hybrid_hint):
            return "hybrid"

        # 2) report only -> report_only
        if has_report:
            return "report_only"

        # 3) chart/graph/plot/visualize -> chart_only
        if has_chart:
            return "chart_only"

        # 4) compare/stats/trend/highest/lowest -> analysis_only
        if has_analysis:
            return "analysis_only"

        # 5) summary/explain/document questions -> rag_only
        if self._contains_any(q, self.RAG_KEYWORDS):
            return "rag_only"

        # Safe default for generic Q&A.
        return "rag_only"

    @staticmethod
    def _contains_any(query: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in query for keyword in keywords)

    @staticmethod
    def _build_response(route: RouteType) -> RouteResponse:
        return RouteResponse(
            route=route,
            needs_rag=route in {"rag_only", "hybrid"},
            needs_analysis=route in {"analysis_only", "hybrid"},
            needs_chart=route in {"chart_only", "hybrid"},
            needs_report=route in {"report_only", "hybrid"},
        )
