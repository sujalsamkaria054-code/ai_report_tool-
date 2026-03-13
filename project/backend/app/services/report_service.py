from __future__ import annotations

from typing import Any

from app.prompts.report_prompt import build_report_prompt
from app.schemas.report_schema import ReportSpec


class ReportService:
    """Build structured professional reports from intermediate pipeline outputs."""

    def build(self, payload: dict[str, Any]) -> ReportSpec:
        query = str(payload.get("query", "")).strip()
        rag_output = str(payload.get("rag_output", "")).strip()
        analysis_output = payload.get("analysis_output", {}) or {}
        charts = payload.get("charts", []) or []

        analysis_summary = self._analysis_summary(analysis_output)
        chart_summary = self._chart_metadata_summary(charts)

        _ = build_report_prompt(
            query=query,
            rag_text=rag_output,
            analysis_summary=analysis_summary,
            chart_summary=chart_summary,
        )

        title = self._build_title(query=query)
        summary = self._build_summary(rag_output=rag_output, analysis_summary=analysis_summary)
        insights = self._build_insights(rag_output=rag_output, analysis_output=analysis_output, charts=charts)
        recommendations = self._build_recommendations(analysis_output=analysis_output, charts=charts)
        conclusion = self._build_conclusion(rag_output=rag_output, analysis_output=analysis_output)

        return ReportSpec(
            title=title,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            conclusion=conclusion,
        )

    @staticmethod
    def _build_title(query: str) -> str:
        if query:
            return f"Analysis Report: {query[:80]}"
        return "Analysis Report"

    @staticmethod
    def _analysis_summary(analysis_output: dict[str, Any]) -> str:
        if analysis_output.get("status") != "ok":
            return "No analytical tables were available."

        items = analysis_output.get("analysis", []) or []
        table_count = len(items)
        numeric_fields = sum(len(item.get("numeric_columns", [])) for item in items)
        return f"Analyzed {table_count} table(s) across {numeric_fields} numeric field(s)."

    @staticmethod
    def _chart_metadata_summary(charts: list[dict[str, Any]]) -> str:
        if not charts:
            return "No charts were generated."
        parts: list[str] = []
        for chart in charts:
            chart_type = chart.get("chart_type", "unknown")
            title = chart.get("title", "Untitled")
            meta = chart.get("meta", {}) or {}
            metric = meta.get("metric")
            suffix = f" ({metric})" if metric else ""
            parts.append(f"{chart_type}: {title}{suffix}")
        return "; ".join(parts)

    def _build_summary(self, rag_output: str, analysis_summary: str) -> str:
        rag_sentence = rag_output if rag_output else "No retrieval context was available."
        return f"{rag_sentence} {analysis_summary}".strip()

    def _build_insights(
        self,
        rag_output: str,
        analysis_output: dict[str, Any],
        charts: list[dict[str, Any]],
    ) -> list[str]:
        insights: list[str] = []

        if rag_output:
            insights.append(f"Context insight: {rag_output[:180]}")

        if analysis_output.get("status") == "ok":
            for table in analysis_output.get("analysis", []) or []:
                table_name = table.get("table_name", "table")
                trends = table.get("trend_detection", {}) or {}
                if trends:
                    trend_text = ", ".join(f"{k}: {v}" for k, v in trends.items())
                    insights.append(f"Trend insight ({table_name}): {trend_text}")

                top_bottom = table.get("top_bottom_values", {}) or {}
                for metric, values in top_bottom.items():
                    top_rows = values.get("top", []) if isinstance(values, dict) else []
                    if top_rows:
                        top_value = top_rows[0].get("value")
                        insights.append(f"Top value insight ({table_name}, {metric}): {top_value}")

        if charts:
            insights.append(f"Visualization insight: {len(charts)} chart(s) prepared for review.")

        if not insights:
            insights.append("No significant insights were detected from the available inputs.")

        return insights[:8]

    @staticmethod
    def _build_recommendations(analysis_output: dict[str, Any], charts: list[dict[str, Any]]) -> list[str]:
        recommendations: list[str] = []

        if analysis_output.get("status") == "ok":
            recommendations.append("Review the detected trends and validate them against recent operational context.")
            recommendations.append("Prioritize metrics with extreme top/bottom values for follow-up action.")
        else:
            recommendations.append("Provide structured table data to unlock quantitative analysis in the next run.")

        if charts:
            recommendations.append("Use generated charts in stakeholder communication for clearer metric storytelling.")

        return recommendations[:5]

    @staticmethod
    def _build_conclusion(rag_output: str, analysis_output: dict[str, Any]) -> str:
        if analysis_output.get("status") == "ok":
            return "The report combines retrieval context and deterministic data analysis for actionable decision support."
        if rag_output:
            return "The report is primarily based on retrieval context; additional tabular data is recommended for deeper analysis."
        return "Insufficient context was available; ingest documents and table data for a complete report."
