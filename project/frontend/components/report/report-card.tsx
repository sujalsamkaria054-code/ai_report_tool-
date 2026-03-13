import type { ReportSpec } from "../../lib/types";
import { InsightList } from "./insight-list";
import { RecommendationList } from "./recommendation-list";

type ReportCardProps = {
  report: ReportSpec;
};

export function ReportCard({ report }: ReportCardProps) {
  return (
    <article
      style={{
        border: "1px solid #dbeafe",
        background: "#eff6ff",
        borderRadius: 8,
        padding: 12,
        display: "grid",
        gap: 12,
      }}
    >
      <header>
        <h4 style={{ margin: 0 }}>Report</h4>
        <h5 style={{ margin: "6px 0 0 0" }}>{report.title}</h5>
      </header>

      <section>
        <h6 style={{ margin: "0 0 4px 0" }}>Summary</h6>
        <p style={{ margin: 0 }}>{report.summary || "No summary provided."}</p>
      </section>

      <section>
        <h6 style={{ margin: "0 0 4px 0" }}>Insights</h6>
        <InsightList insights={report.insights} />
      </section>

      <section>
        <h6 style={{ margin: "0 0 4px 0" }}>Recommendations</h6>
        <RecommendationList recommendations={report.recommendations} />
      </section>

      <section>
        <h6 style={{ margin: "0 0 4px 0" }}>Conclusion</h6>
        <p style={{ margin: 0 }}>{report.conclusion || "No conclusion provided."}</p>
      </section>
    </article>
  );
}
