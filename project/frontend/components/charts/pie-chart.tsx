import type { ChartSpec } from "../../lib/types";

type PieChartProps = {
  chart: ChartSpec;
};

export function PieChart({ chart }: PieChartProps) {
  const labels = chart.labels;
  const values = chart.values;

  if (labels.length === 0 || values.length === 0) {
    return <p>Pie chart data is unavailable.</p>;
  }

  const total = values.reduce((acc, value) => acc + value, 0) || 1;

  return (
    <div>
      <strong>{chart.title || "Pie Chart"}</strong>
      <ul style={{ marginTop: 8, paddingLeft: 18 }}>
        {labels.map((label, idx) => {
          const value = values[idx] ?? 0;
          const pct = ((value / total) * 100).toFixed(1);
          return (
            <li key={`${label}-${idx}`}>
              {label}: {value} ({pct}%)
            </li>
          );
        })}
      </ul>
    </div>
  );
}
