from dataclasses import dataclass, field
from typing import Callable

from app.agents.analysis_agent import AnalysisAgent
from app.agents.chart_agent import ChartAgent
from app.agents.formatter_agent import FormatterAgent
from app.agents.rag_agent import RagAgent
from app.agents.report_agent import ReportAgent
from app.agents.router_agent import RouterAgent
from app.graph.routes import GraphRoutes
from app.graph.state import GraphState
from app.schemas.report_schema import ReportSpec
from app.schemas.route_schema import RouteType
from app.schemas.table_schema import TableSpec

NodeFn = Callable[[GraphState], GraphState]


@dataclass
class OrchestrationGraph:
    """Lightweight LangGraph-style orchestrator with conditional routing."""

    routes: GraphRoutes = field(default_factory=GraphRoutes)
    router_agent: RouterAgent = field(default_factory=RouterAgent)
    rag_agent: RagAgent = field(default_factory=RagAgent)
    analysis_agent: AnalysisAgent = field(default_factory=AnalysisAgent)
    chart_agent: ChartAgent = field(default_factory=ChartAgent)
    report_agent: ReportAgent = field(default_factory=ReportAgent)
    formatter_agent: FormatterAgent = field(default_factory=FormatterAgent)

    def invoke(
        self,
        query: str,
        document_id: str | None = None,
        tables: list[TableSpec] | None = None,
        sources: list[str] | None = None,
    ) -> GraphState:
        state = GraphState(user_query=query, document_id=document_id)
        if document_id:
            state.sources.append(f"document://{document_id}")
        if tables:
            state.tables = tables
        if sources:
            state.sources.extend(source for source in sources if source not in state.sources)

        state = self._router_node(state)

        route = state.route
        if route is None:
            state.errors.append("Router did not return a route.")
            return self._formatter_node(state)

        # Path resolution is explicit so report-focused routes can be enriched with
        # retrieval + analysis when document/table context is available.
        for node_name in self._resolve_path(state=state, route=route):
            node = self._nodes()[node_name]
            state = node(state)

        return state

    def _nodes(self) -> dict[str, NodeFn]:
        return {
            "rag": self._rag_node,
            "analysis": self._analysis_node,
            "chart": self._chart_node,
            "report": self._report_node,
            "formatter": self._formatter_node,
        }

    def _resolve_path(self, state: GraphState, route: RouteType) -> list[str]:
        base_path = list(self.routes.get_path(route))

        if route != "report_only":
            return base_path

        # Report quality drops when report-only bypasses upstream context.
        # Ensure report requests always include retrieval context.
        if "rag" not in base_path:
            base_path.insert(0, "rag")

        # If normalized table data is present, enrich report-only with analysis
        # so the report receives structured analysis summary fields.
        if self._has_normalized_tables(state) and "analysis" not in base_path:
            report_idx = base_path.index("report") if "report" in base_path else len(base_path)
            base_path.insert(report_idx, "analysis")

        return base_path

    @staticmethod
    def _has_normalized_tables(state: GraphState) -> bool:
        for table in state.tables:
            if not table.name:
                continue
            if not isinstance(table.columns, list) or not table.columns:
                continue
            if not isinstance(table.rows, list):
                continue
            return True
        return False

    def _router_node(self, state: GraphState) -> GraphState:
        router_result = self.router_agent.run(state.user_query)
        state.route = router_result.route
        state.router_output = router_result.model_dump()
        return state

    def _rag_node(self, state: GraphState) -> GraphState:
        state.rag_output = self.rag_agent.run(state.user_query)
        return state

    def _analysis_node(self, state: GraphState) -> GraphState:
        payload = {
            "query": state.user_query,
            "rag_output": state.rag_output,
            "tables": [table.model_dump() for table in state.tables],
        }
        state.analysis_output = self.analysis_agent.run(payload)
        return state

    def _chart_node(self, state: GraphState) -> GraphState:
        chart_payload = self.chart_agent.run(
            {
                "analysis": state.analysis_output,
                "tables": [table.model_dump() for table in state.tables],
            }
        )
        state.chart_output = chart_payload if isinstance(chart_payload, list) else []
        return state

    def _report_node(self, state: GraphState) -> GraphState:
        report_payload = self.report_agent.run(
            {
                "query": state.user_query,
                "rag_output": state.rag_output,
                "analysis_output": state.analysis_output,
                "tables": [table.model_dump() for table in state.tables],
                "charts": [chart.model_dump() for chart in state.chart_output],
            }
        )

        if isinstance(report_payload, ReportSpec):
            state.report_output = report_payload
        else:
            state.report_output = ReportSpec(
                title="Generated Report",
                summary=str(report_payload) if report_payload else "",
                insights=[],
                recommendations=[],
                conclusion="",
            )
        return state

    def _formatter_node(self, state: GraphState) -> GraphState:
        formatted = self.formatter_agent.run(
            {
                "route": state.route,
                "content": state.rag_output,
                "charts": [chart.model_dump() for chart in state.chart_output],
                "tables": [table.model_dump() for table in state.tables],
                "report": state.report_output.model_dump() if state.report_output else None,
                "sources": state.sources,
                "errors": state.errors,
            }
        )
        state.formatter_output = formatted if isinstance(formatted, dict) else {}
        return state


def build_graph(**kwargs) -> OrchestrationGraph:
    """Create an executable graph object with START -> Router -> conditional nodes."""
    return OrchestrationGraph(**kwargs)
