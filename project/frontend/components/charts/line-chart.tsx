import type { ChartSpec } from "../../lib/types";

type LineChartProps = {
  chart: ChartSpec;
};

export function LineChart({ chart }: LineChartProps) {
  const series = chart.series[0];
  const labels = chart.x_axis;

  if (!series || labels.length === 0 || series.values.length === 0) {
    return <p>Line chart data is unavailable.</p>;
  }

  return (
    <div>
      <strong>{chart.title || "Line Chart"}</strong>
      <ol style={{ marginTop: 8, paddingLeft: 18 }}>
        {labels.map((label, idx) => {
          const value = series.values[idx] ?? 0;
          return (
            <li key={`${label}-${idx}`}>
              {label}: {value}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
