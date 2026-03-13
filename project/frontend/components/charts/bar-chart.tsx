import type { ChartSpec } from "../../lib/types";

type BarChartProps = {
  chart: ChartSpec;
};

export function BarChart({ chart }: BarChartProps) {
  const series = chart.series[0];
  const labels = chart.x_axis;

  if (!series || labels.length === 0 || series.values.length === 0) {
    return <p>Bar chart data is unavailable.</p>;
  }

  const maxValue = Math.max(...series.values, 1);

  return (
    <div>
      <strong>{chart.title || "Bar Chart"}</strong>
      <ul style={{ listStyle: "none", padding: 0, marginTop: 8 }}>
        {labels.map((label, idx) => {
          const value = series.values[idx] ?? 0;
          const widthPercent = Math.max(4, (value / maxValue) * 100);
          return (
            <li key={`${label}-${idx}`} style={{ marginBottom: 8 }}>
              <div style={{ fontSize: 12 }}>{label}</div>
              <div
                style={{
                  background: "#3b82f6",
                  height: 12,
                  width: `${widthPercent}%`,
                  borderRadius: 4,
                }}
                title={`${label}: ${value}`}
              />
            </li>
          );
        })}
      </ul>
    </div>
  );
}
