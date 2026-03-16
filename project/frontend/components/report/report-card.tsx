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
        border: "1px solid #bfdbfe",
        background: "linear-gradient(180deg, #eff6ff 0%, #f8fafc 100%)",
        borderRadius: 12,
        padding: 14,
        display: "grid",
        gap: 12,
      }}
    >
      <div>
        <h3 style={{ margin: 0, fontSize: 16, color: "#0f172a" }}>{report.title || "Report"}</h3>
        <p style={{ margin: "6px 0 0", color: "#334155", fontSize: 13, lineHeight: 1.5 }}>{report.summary}</p>
      </div>

      <section style={{ display: "grid", gap: 8 }}>
        <h4 style={{ margin: 0, fontSize: 13, color: "#1e3a8a" }}>Insights</h4>
        <InsightList insights={report.insights} />
      </section>

      <section style={{ display: "grid", gap: 8 }}>
        <h4 style={{ margin: 0, fontSize: 13, color: "#1e3a8a" }}>Recommendations</h4>
        <RecommendationList recommendations={report.recommendations} />
      </section>

      <section style={{ borderTop: "1px solid #dbeafe", paddingTop: 10 }}>
        <h4 style={{ margin: 0, fontSize: 13, color: "#1e3a8a" }}>Conclusion</h4>
        <p style={{ margin: "6px 0 0", color: "#334155", fontSize: 13, lineHeight: 1.5 }}>{report.conclusion}</p>
      </section>
    </article>
  );
}
