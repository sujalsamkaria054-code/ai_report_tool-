import { ChartRenderer } from "../charts/chart-renderer";
import { ReportCard } from "../report/report-card";
import { DataTable } from "../tables/data-table";
import type { ChatMessage } from "../../lib/types";

type MessageCardProps = {
  message: ChatMessage;
};

export function MessageCard({ message }: MessageCardProps) {
  const response = message.response;

  return (
    <article
      style={{
        border: "1px solid #ddd",
        borderRadius: 8,
        padding: 12,
        marginBottom: 10,
        background: message.role === "assistant" ? "#f8fbff" : "#ffffff",
      }}
    >
      <strong style={{ textTransform: "capitalize" }}>{message.role}</strong>
      <p style={{ margin: "8px 0" }}>{message.content}</p>

      {response?.report && (
        <section style={{ marginTop: 8 }}>
          <ReportCard report={response.report} />
        </section>
      )}

      {response && (
        <section style={{ marginTop: 8 }}>
          <h4>Charts</h4>
          <ChartRenderer charts={response.charts} />
        </section>
      )}

      {response && (
        <section style={{ marginTop: 8 }}>
          <h4>Tables</h4>
          {response.tables.length === 0 ? (
            <p style={{ margin: 0, color: "#6b7280" }}>No tables available.</p>
          ) : (
            <div style={{ display: "grid", gap: 10 }}>
              {response.tables.map((table, index) => (
                <DataTable
                  key={`${table.name}-${index}`}
                  title={table.name || `Table ${index + 1}`}
                  columns={table.columns}
                  rows={table.rows}
                />
              ))}
            </div>
          )}
        </section>
      )}

      {response && response.sources.length > 0 && (
        <section style={{ marginTop: 8 }}>
          <h4>Sources</h4>
          <ul>
            {response.sources.map((source) => (
              <li key={source}>{source}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}
