import type { ChartSpec } from "../../lib/types";

type LineChartProps = {
  chart: ChartSpec;
};

export function LineChart({ chart }: LineChartProps) {
  const values = chart.series[0]?.values ?? [];
  const xAxis = chart.x_axis ?? [];

  if (xAxis.length === 0 || values.length === 0) {
    return <p style={{ margin: 0, color: "#64748b", fontSize: 12 }}>Line chart data unavailable.</p>;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <strong style={{ fontSize: 13 }}>{chart.title || "Line Chart"}</strong>
      <div style={{ display: "grid", gap: 5 }}>
        {xAxis.map((label, idx) => {
          const value = values[idx] ?? 0;
          const normalized = ((value - min) / range) * 100;
          return (
            <div key={`${label}-${idx}`} style={{ display: "grid", gridTemplateColumns: "90px 1fr 56px", gap: 8 }}>
              <span style={{ fontSize: 12, color: "#475569", overflow: "hidden", textOverflow: "ellipsis" }}>
                {label}
              </span>
              <div style={{ height: 6, borderRadius: 999, background: "#e2e8f0", alignSelf: "center" }}>
                <div style={{ height: "100%", width: `${Math.max(normalized, 2)}%`, background: "#14b8a6", borderRadius: 999 }} />
              </div>
              <span style={{ fontSize: 12, color: "#0f172a", textAlign: "right" }}>{value}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
