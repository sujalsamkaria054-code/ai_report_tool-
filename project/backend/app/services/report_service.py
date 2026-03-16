from __future__ import annotations

from typing import Any

from app.prompts.report_prompt import build_report_prompt
from app.schemas.report_schema import ReportSpec


class ReportService:
    """Build concise business reports grounded in retrieved and analyzed data."""

    def build(self, payload: dict[str, Any]) -> ReportSpec:
        query = str(payload.get("query", "")).strip()
        rag_output = self._sanitize_text(payload.get("rag_output", ""))
        analysis_output = payload.get("analysis_output", {}) or {}
        tables = payload.get("tables", []) or []
        charts = payload.get("charts", []) or []

        analysis_summary = self._analysis_summary(analysis_output)
        table_summary = self._table_summary(tables)
        chart_summary = self._chart_metadata_summary(charts)

        # Prompt is constructed so providers can be plugged in later with the same grounded contract.
        _ = build_report_prompt(
            query=query,
            rag_text=rag_output,
            analysis_summary=analysis_summary,
            table_summary=table_summary,
            chart_summary=chart_summary,
        )

        limitations = self._limitations(rag_output=rag_output, analysis_output=analysis_output, tables=tables)

        return ReportSpec(
            title=self._build_title(query=query, rag_output=rag_output),
            summary=self._build_summary(
                query=query,
                rag_output=rag_output,
                analysis_summary=analysis_summary,
                limitations=limitations,
            ),
            insights=self._build_insights(
                rag_output=rag_output,
                analysis_output=analysis_output,
                table_summary=table_summary,
                charts=charts,
                limitations=limitations,
            ),
            recommendations=self._build_recommendations(
                analysis_output=analysis_output,
                rag_output=rag_output,
                limitations=limitations,
            ),
            conclusion=self._build_conclusion(limitations=limitations),
        )

    @staticmethod
    def _sanitize_text(value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        # Remove obvious low-value scaffold phrasing and raw table-like dumps.
        text = text.replace("Based on retrieved context,", "").strip()
        return text[:500]

    def _build_title(self, query: str, rag_output: str) -> str:
        subject = self._detect_subject(rag_output)
        if subject:
            return f"Business Report: {subject}"
        if query:
            trimmed = query[:80].rstrip(" ?.!")
            return f"Business Report: {trimmed}"
        return "Business Report"

    @staticmethod
    def _detect_subject(rag_output: str) -> str:
        if not rag_output:
            return ""
        sentences = [part.strip() for part in rag_output.replace("\n", " ").split(".") if part.strip()]
        return sentences[0][:72] if sentences else ""

    @staticmethod
    def _analysis_summary(analysis_output: dict[str, Any]) -> str:
        summary = analysis_output.get("summary", {}) or {}
        if analysis_output.get("status") != "ok":
            return "Quantitative analysis was not available from the extracted tables."

        table_count = int(summary.get("table_count", 0) or 0)
        readable_count = int(summary.get("readable_table_count", 0) or 0)
        numeric_count = int(summary.get("numeric_field_count", 0) or 0)

        if table_count == 0:
            return "No tables were available for quantitative analysis."

        return (
            f"{readable_count} of {table_count} table(s) were readable, "
            f"with {numeric_count} numeric field(s) detected."
        )

    @staticmethod
    def _table_summary(tables: list[dict[str, Any]]) -> str:
        if not tables:
            return "No extracted tables were provided to the report stage."

        safe_items: list[str] = []
        for index, table in enumerate(tables, start=1):
            name = str(table.get("name") or f"table_{index}")
            row_count = int(table.get("row_count") or len(table.get("rows") or []) or 0)
            column_count = len(table.get("columns") or [])
            safe_items.append(f"{name}: {row_count} row(s), {column_count} column(s)")
        return "; ".join(safe_items[:5])

    @staticmethod
    def _chart_metadata_summary(charts: list[dict[str, Any]]) -> str:
        if not charts:
            return "No charts were generated."
        parts: list[str] = []
        for chart in charts:
            chart_type = chart.get("chart_type", "unknown")
            title = chart.get("title", "Untitled")
            parts.append(f"{chart_type}: {title}")
        return "; ".join(parts)

    def _limitations(self, rag_output: str, analysis_output: dict[str, Any], tables: list[dict[str, Any]]) -> list[str]:
        limitations: list[str] = []
        summary = analysis_output.get("summary", {}) or {}

        if not rag_output or "could not find relevant context" in rag_output.lower():
            limitations.append("Document retrieval did not return strong supporting context.")

        table_count = int(summary.get("table_count", 0) or len(tables))
        readable_count = int(summary.get("readable_table_count", 0))
        numeric_count = int(summary.get("numeric_field_count", 0))

        if table_count > 0 and readable_count == 0:
            limitations.append("Extracted tables were not readable for analysis.")
        if table_count == 0:
            limitations.append("No usable table data was available in the document.")
        if numeric_count == 0:
            limitations.append("No numeric fields were available for metric analysis.")

        for warning in (summary.get("warnings") or []):
            warning_text = str(warning).strip()
            if warning_text:
                limitations.append(warning_text)

        return limitations[:4]

    def _build_summary(self, query: str, rag_output: str, analysis_summary: str, limitations: list[str]) -> str:
        query_line = f"Request focus: {query}." if query else "Request focus was not explicitly provided."
        context_line = (
            f"Key context found: {rag_output[:220]}." if rag_output else "Key context found: limited document context."
        )
        limitation_line = (
            f"Limitation: {limitations[0]}" if limitations else "Data quality was sufficient for a baseline business summary."
        )
        return f"{query_line} {context_line} {analysis_summary} {limitation_line}".strip()

    def _build_insights(
        self,
        rag_output: str,
        analysis_output: dict[str, Any],
        table_summary: str,
        charts: list[dict[str, Any]],
        limitations: list[str],
    ) -> list[str]:
        summary = analysis_output.get("summary", {}) or {}
        insights: list[str] = []

        if rag_output:
            insights.append(f"Document context indicates: {rag_output[:180]}")

        readable = int(summary.get("readable_table_count", 0) or 0)
        tables = int(summary.get("table_count", 0) or 0)
        numeric_fields = summary.get("numeric_fields", []) or []
        date_fields = summary.get("date_fields", []) or []
        categories = summary.get("category_fields", []) or []

        if tables:
            insights.append(f"Tabular coverage: {readable}/{tables} table(s) readable ({table_summary}).")
        if numeric_fields:
            insights.append(f"Primary measurable fields: {', '.join(map(str, numeric_fields[:4]))}.")
        if date_fields:
            insights.append(f"Time-oriented tracking appears possible using: {', '.join(map(str, date_fields[:3]))}.")
        if categories:
            insights.append(f"Category segmentation is available via: {', '.join(map(str, categories[:3]))}.")

        if charts:
            insights.append(f"{len(charts)} chart candidate(s) can support stakeholder communication.")

        if limitations:
            insights.append(f"Data limitation noted: {limitations[0]}")

        if not insights:
            insights.append("Available evidence is limited; this report reflects only partial document signals.")

        return insights[:6]

    @staticmethod
    def _build_recommendations(
        analysis_output: dict[str, Any],
        rag_output: str,
        limitations: list[str],
    ) -> list[str]:
        recommendations: list[str] = []

        summary = analysis_output.get("summary", {}) or {}
        key_metrics = summary.get("key_metrics", []) or []
        chart_candidates = summary.get("chart_candidates", []) or []

        if key_metrics:
            metrics = [str(metric.get("field")) for metric in key_metrics[:3] if metric.get("field")]
            if metrics:
                recommendations.append(
                    f"Prioritize routine monitoring for these metrics: {', '.join(metrics)}."
                )

        if chart_candidates:
            recommendations.append("Use the proposed chart candidates to communicate trends and category performance.")

        if not rag_output:
            recommendations.append("Re-run retrieval with more specific business terms to improve contextual grounding.")

        if limitations:
            recommendations.append("Address data limitations before high-impact decisions are made.")

        if not recommendations:
            recommendations.append("Maintain current tracking cadence and validate findings against upcoming reporting periods.")

        return recommendations[:4]

    @staticmethod
    def _build_conclusion(limitations: list[str]) -> str:
        if limitations:
            return (
                "This is a partial business report grounded in available context and structured analysis; "
                "additional clean data would improve confidence."
            )
        return "This report is grounded in retrieved context and structured analysis and is suitable for baseline planning."
