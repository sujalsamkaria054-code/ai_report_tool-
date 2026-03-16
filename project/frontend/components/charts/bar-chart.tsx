import type { ChartSpec } from "../../lib/types";

type BarChartProps = {
  chart: ChartSpec;
};

export function BarChart({ chart }: BarChartProps) {
  const points = chart.series[0]?.values ?? [];
  const labels = chart.x_axis ?? [];

  if (labels.length === 0 || points.length === 0) {
    return <p style={{ margin: 0, color: "#64748b", fontSize: 12 }}>Bar chart data unavailable.</p>;
  }

  const max = Math.max(...points, 1);

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <strong style={{ fontSize: 13 }}>{chart.title || "Bar Chart"}</strong>
      <div style={{ display: "grid", gap: 6 }}>
        {labels.map((label, idx) => {
          const value = points[idx] ?? 0;
          const pct = Math.min((value / max) * 100, 100);
          return (
            <div key={`${label}-${idx}`} style={{ display: "grid", gap: 2 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                <span style={{ color: "#334155" }}>{label}</span>
                <span style={{ color: "#0f172a" }}>{value}</span>
              </div>
              <div style={{ height: 8, borderRadius: 999, background: "#e2e8f0" }}>
                <div style={{ height: "100%", width: `${pct}%`, background: "#2563eb", borderRadius: 999 }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
