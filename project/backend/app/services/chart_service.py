from __future__ import annotations

from typing import Any

from app.schemas.chart_schema import ChartSeries, ChartSpec
from app.utils.logger import get_logger


logger = get_logger(__name__)


class ChartService:
    """Create frontend-safe charts only from normalized tables + analysis summary candidates."""

    MAX_CATEGORY_FOR_BAR = 20
    MAX_CATEGORY_FOR_PIE = 8

    def generate_charts(self, payload: dict[str, Any]) -> list[ChartSpec]:
        if not isinstance(payload, dict):
            return []

        analysis_result = payload.get("analysis", {}) or {}
        tables = payload.get("tables", []) or []

        if analysis_result.get("status") != "ok":
            return []

        summary = analysis_result.get("summary", {}) or {}
        candidates = summary.get("chart_candidates", []) or []
        logger.info("Chart generation input | candidate_count=%d", len(candidates))
        if not candidates:
            return []

        specs: list[ChartSpec] = []
        used_signatures: set[str] = set()

        for candidate in candidates:
            spec = self._build_from_candidate(candidate=candidate, tables=tables)
            if spec is None:
                continue

            signature = self._spec_signature(spec)
            if signature in used_signatures:
                continue
            used_signatures.add(signature)
            specs.append(spec)

        logger.info("Chart generation output | generated=%d", len(specs))
        return specs

    def _build_from_candidate(self, candidate: dict[str, Any], tables: list[dict[str, Any]]) -> ChartSpec | None:
        if not isinstance(candidate, dict):
            return None

        chart_type = str(candidate.get("type", "")).strip().lower()
        metric = str(candidate.get("y") or candidate.get("value") or "").strip()
        x_field = str(candidate.get("x") or candidate.get("category") or "").strip()

        if chart_type not in {"line", "bar", "pie"}:
            return None
        if not metric or not x_field:
            return None

        selection = self._select_table_records(tables=tables, x_field=x_field, metric=metric)
        if selection is None:
            return None

        table_name, records = selection
        if chart_type == "line":
            return self._line_chart(table_name=table_name, x_field=x_field, metric=metric, records=records)
        if chart_type == "bar":
            return self._bar_chart(table_name=table_name, x_field=x_field, metric=metric, records=records)
        return self._pie_chart(table_name=table_name, category=x_field, metric=metric, records=records)

    @staticmethod
    def _select_table_records(
        tables: list[dict[str, Any]],
        x_field: str,
        metric: str,
    ) -> tuple[str, list[dict[str, Any]]] | None:
        for index, table in enumerate(tables, start=1):
            if not isinstance(table, dict):
                continue
            rows = table.get("rows") or []
            if not rows or not isinstance(rows, list):
                continue

            safe_rows: list[dict[str, Any]] = [row for row in rows if isinstance(row, dict)]
            if not safe_rows:
                continue

            first_row = safe_rows[0]
            if x_field not in first_row or metric not in first_row:
                continue

            table_name = str(table.get("name") or f"table_{index}")
            return table_name, safe_rows
        return None

    def _line_chart(
        self,
        table_name: str,
        x_field: str,
        metric: str,
        records: list[dict[str, Any]],
    ) -> ChartSpec | None:
        points = self._valid_points(records=records, label_field=x_field, metric_field=metric)
        if len(points) < 2:
            return None

        labels = [label for label, _ in points]
        values = [value for _, value in points]

        return ChartSpec(
            chart_type="line",
            title=f"{table_name}: {metric} over {x_field}",
            x_axis=labels,
            series=[ChartSeries(name=metric, values=values)],
            meta={"table": table_name, "x": x_field, "y": metric},
        )

    def _bar_chart(
        self,
        table_name: str,
        x_field: str,
        metric: str,
        records: list[dict[str, Any]],
    ) -> ChartSpec | None:
        grouped = self._group_numeric(records=records, category_field=x_field, metric_field=metric)
        if not grouped:
            return None

        if len(grouped) > self.MAX_CATEGORY_FOR_BAR:
            return None

        labels = list(grouped.keys())
        values = [grouped[label] for label in labels]

        return ChartSpec(
            chart_type="bar",
            title=f"{table_name}: {metric} by {x_field}",
            x_axis=labels,
            series=[ChartSeries(name=metric, values=values)],
            meta={"table": table_name, "x": x_field, "y": metric},
        )

    def _pie_chart(
        self,
        table_name: str,
        category: str,
        metric: str,
        records: list[dict[str, Any]],
    ) -> ChartSpec | None:
        grouped = self._group_numeric(records=records, category_field=category, metric_field=metric)
        if not grouped:
            return None

        if len(grouped) < 2 or len(grouped) > self.MAX_CATEGORY_FOR_PIE:
            return None

        total = sum(grouped.values())
        if total <= 0:
            return None

        labels = list(grouped.keys())
        values = [grouped[label] for label in labels]

        return ChartSpec(
            chart_type="pie",
            title=f"{table_name}: {metric} distribution by {category}",
            labels=labels,
            values=values,
            meta={"table": table_name, "category": category, "value": metric},
        )

    @staticmethod
    def _valid_points(records: list[dict[str, Any]], label_field: str, metric_field: str) -> list[tuple[str, float]]:
        points: list[tuple[str, float]] = []
        for row in records:
            if not isinstance(row, dict):
                continue

            label_value = row.get(label_field)
            metric_value = ChartService._to_number(row.get(metric_field))
            if label_value is None or metric_value is None:
                continue

            label = str(label_value).strip()
            if not label:
                continue
            points.append((label, metric_value))
        return points

    @staticmethod
    def _group_numeric(records: list[dict[str, Any]], category_field: str, metric_field: str) -> dict[str, float]:
        grouped: dict[str, float] = {}
        for row in records:
            if not isinstance(row, dict):
                continue

            category_value = row.get(category_field)
            metric_value = ChartService._to_number(row.get(metric_field))
            if category_value is None or metric_value is None:
                continue

            key = str(category_value).strip()
            if not key:
                continue

            grouped[key] = grouped.get(key, 0.0) + metric_value

        # Preserve deterministic ordering by descending metric then key.
        sorted_items = sorted(grouped.items(), key=lambda item: (-item[1], item[0]))
        return dict(sorted_items)

    @staticmethod
    def _to_number(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            casted = float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None
        return casted

    @staticmethod
    def _spec_signature(spec: ChartSpec) -> str:
        return f"{spec.chart_type}|{spec.title}|{spec.meta}"
