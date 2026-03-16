import type { ChartSpec } from "../../lib/types";
import { BarChart } from "./bar-chart";
import { LineChart } from "./line-chart";
import { PieChart } from "./pie-chart";

type ChartRendererProps = {
  charts: ChartSpec[];
};

export function ChartRenderer({ charts }: ChartRendererProps) {
  if (charts.length === 0) return null;

  return (
    <section style={{ display: "grid", gap: 10 }}>
      <h4 style={{ margin: 0, fontSize: 13, color: "#334155" }}>Charts</h4>
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
        {charts.map((chart, index) => (
          <div
            key={`${chart.title}-${chart.chart_type}-${index}`}
            style={{
              border: "1px solid #e2e8f0",
              borderRadius: 10,
              padding: 10,
              background: "#ffffff",
            }}
          >
            {chart.chart_type === "line" ? <LineChart chart={chart} /> : null}
            {chart.chart_type === "bar" ? <BarChart chart={chart} /> : null}
            {chart.chart_type === "pie" ? <PieChart chart={chart} /> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
