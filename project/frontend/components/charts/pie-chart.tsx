import type { ChartSpec } from "../../lib/types";

type PieChartProps = {
  chart: ChartSpec;
};

export function PieChart({ chart }: PieChartProps) {
  const labels = chart.labels ?? [];
  const values = chart.values ?? [];

  if (labels.length === 0 || values.length === 0) {
    return <p style={{ margin: 0, color: "#64748b", fontSize: 12 }}>Pie chart data unavailable.</p>;
  }

  const total = values.reduce((acc, value) => acc + value, 0) || 1;

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <strong style={{ fontSize: 13 }}>{chart.title || "Pie Chart"}</strong>
      <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 4 }}>
        {labels.map((label, idx) => {
          const value = values[idx] ?? 0;
          const pct = ((value / total) * 100).toFixed(1);
          return (
            <li key={`${label}-${idx}`} style={{ fontSize: 12, color: "#334155" }}>
              {label}: {value} ({pct}%)
            </li>
          );
        })}
      </ul>
    </div>
  );
}
