import type { ChartSpec } from "../../lib/types";
import { BarChart } from "./bar-chart";
import { LineChart } from "./line-chart";
import { PieChart } from "./pie-chart";

type ChartRendererProps = {
  charts: ChartSpec[];
};

function RenderSingleChart({ chart }: { chart: ChartSpec }) {
  if (chart.chart_type === "bar") return <BarChart chart={chart} />;
  if (chart.chart_type === "line") return <LineChart chart={chart} />;
  if (chart.chart_type === "pie") return <PieChart chart={chart} />;
  return <p>Unsupported chart type.</p>;
}

export function ChartRenderer({ charts }: ChartRendererProps) {
  if (!charts.length) {
    return <p>No charts available.</p>;
  }

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {charts.map((chart, index) => (
        <section key={`${chart.title}-${index}`} style={{ border: "1px solid #e5e7eb", padding: 8 }}>
          <RenderSingleChart chart={chart} />
        </section>
      ))}
    </div>
  );
}
