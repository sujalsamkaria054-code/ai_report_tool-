from __future__ import annotations

from typing import Any

from app.schemas.chart_schema import ChartSeries, ChartSpec


class ChartService:
    """Build frontend-friendly chart specs from structured analysis output."""

    TIME_KEYWORDS = {"date", "day", "week", "month", "quarter", "year", "time"}
    PROPORTION_KEYWORDS = {"share", "ratio", "percent", "percentage", "distribution", "portion", "breakdown"}

    def generate_charts(self, analysis_result: dict[str, Any]) -> list[ChartSpec]:
        tables = analysis_result.get("analysis", []) if isinstance(analysis_result, dict) else []
        specs: list[ChartSpec] = []

        for table in tables:
            table_name = str(table.get("table_name", "Analysis"))
            grouped = table.get("grouped_aggregations", {}) or {}
            rows = grouped.get("rows", []) or []
            group_by = str(grouped.get("group_by", "category"))
            numeric_cols = list(table.get("numeric_columns", []))

            if rows and numeric_cols:
                chosen_metric = self._choose_metric(rows[0], numeric_cols)
                if chosen_metric:
                    chart_type = self._select_chart_type(
                        group_by=group_by,
                        metric=chosen_metric,
                        table_name=table_name,
                        row_count=len(rows),
                    )
                    spec = self._build_grouped_spec(
                        chart_type=chart_type,
                        title=f"{table_name} - {chosen_metric}",
                        group_by=group_by,
                        metric=chosen_metric,
                        rows=rows,
                    )
                    specs.append(spec)
                    continue

            top_bottom = table.get("top_bottom_values", {}) or {}
            fallback = self._build_top_bottom_spec(table_name=table_name, top_bottom=top_bottom)
            if fallback is not None:
                specs.append(fallback)

        return specs

    def _select_chart_type(self, group_by: str, metric: str, table_name: str, row_count: int) -> str:
        candidate = " ".join([group_by, metric, table_name]).lower()
        if any(keyword in candidate for keyword in self.TIME_KEYWORDS):
            return "line"
        if any(keyword in candidate for keyword in self.PROPORTION_KEYWORDS):
            return "pie"
        if row_count <= 8:
            return "bar"
        return "bar"

    @staticmethod
    def _choose_metric(first_row: dict[str, Any], numeric_columns: list[str]) -> str | None:
        for column in numeric_columns:
            for suffix in ("_sum", "_mean", "_count"):
                key = f"{column}{suffix}"
                if key in first_row:
                    return key
            if column in first_row:
                return column
        return None

    def _build_grouped_spec(
        self,
        chart_type: str,
        title: str,
        group_by: str,
        metric: str,
        rows: list[dict[str, Any]],
    ) -> ChartSpec:
        labels = [str(row.get(group_by, "")) for row in rows]
        values = [self._to_number(row.get(metric, 0)) for row in rows]

        if chart_type == "pie":
            return ChartSpec(
                chart_type="pie",
                title=title,
                labels=labels,
                values=values,
                meta={"group_by": group_by, "metric": metric},
            )

        return ChartSpec(
            chart_type="line" if chart_type == "line" else "bar",
            title=title,
            x_axis=labels,
            series=[ChartSeries(name=metric, values=values)],
            meta={"group_by": group_by, "metric": metric},
        )

    def _build_top_bottom_spec(self, table_name: str, top_bottom: dict[str, Any]) -> ChartSpec | None:
        if not top_bottom:
            return None

        metric, payload = next(iter(top_bottom.items()))
        top_rows = payload.get("top", []) if isinstance(payload, dict) else []
        if not top_rows:
            return None

        labels = [f"row_{entry.get('row_index', idx)}" for idx, entry in enumerate(top_rows, start=1)]
        values = [self._to_number(entry.get("value", 0)) for entry in top_rows]

        return ChartSpec(
            chart_type="bar",
            title=f"{table_name} - Top {metric}",
            x_axis=labels,
            series=[ChartSeries(name=metric, values=values)],
            meta={"source": "top_bottom_values"},
        )

    @staticmethod
    def _to_number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
