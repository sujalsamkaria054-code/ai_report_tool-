import { ChartRenderer } from "../charts/chart-renderer";
import { ReportCard } from "../report/report-card";
import { DataTable } from "../tables/data-table";
import { SourceList } from "./source-list";
import type { ChatMessage } from "../../lib/types";

type MessageCardProps = {
  message: ChatMessage;
};

export function MessageCard({ message }: MessageCardProps) {
  const response = message.response;
  const isAssistant = message.role === "assistant";

  const charts = Array.isArray(response?.charts) ? response?.charts : [];
  const tables = Array.isArray(response?.tables) ? response?.tables : [];
  const sources = Array.isArray(response?.sources) ? response?.sources : [];

  return (
    <article
      style={{
        alignSelf: isAssistant ? "stretch" : "flex-end",
        maxWidth: isAssistant ? "100%" : "76%",
        background: isAssistant ? "#ffffff" : "#0f172a",
        color: isAssistant ? "#0f172a" : "#ffffff",
        border: isAssistant ? "1px solid #e2e8f0" : "1px solid #0f172a",
        borderRadius: 14,
        padding: 14,
        display: "grid",
        gap: 12,
        boxShadow: isAssistant ? "0 4px 12px rgba(15,23,42,0.06)" : "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong style={{ textTransform: "capitalize", fontSize: 13 }}>{message.role}</strong>
      </div>

      <p style={{ margin: 0, whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{message.content}</p>

      {response?.report ? <ReportCard report={response.report} /> : null}

      {charts.length > 0 ? <ChartRenderer charts={charts} /> : null}

      {tables.length > 0 ? (
        <section style={{ display: "grid", gap: 10 }}>
          <h4 style={{ margin: 0, fontSize: 13, color: "#334155" }}>Tables</h4>
          {tables.map((table, index) => (
            <DataTable
              key={`${table.name}-${index}`}
              title={table.name || `Table ${index + 1}`}
              columns={Array.isArray(table.columns) ? table.columns : []}
              rows={Array.isArray(table.rows) ? table.rows : []}
            />
          ))}
        </section>
      ) : null}

      <SourceList sources={sources} />
    </article>
  );
}
