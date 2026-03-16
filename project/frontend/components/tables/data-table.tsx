type DataTableProps = {
  title?: string;
  columns?: string[];
  rows: Array<Record<string, unknown>>;
};

function deriveColumns(rows: Array<Record<string, unknown>>): string[] {
  const set = new Set<string>();
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      set.add(key);
    }
  }
  return Array.from(set);
}

export function DataTable({ title, columns, rows }: DataTableProps) {
  if (!rows.length) {
    return (
      <section style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 10, background: "#fff" }}>
        {title ? <h5 style={{ margin: "0 0 6px 0", fontSize: 13 }}>{title}</h5> : null}
        <p style={{ margin: 0, color: "#6b7280", fontSize: 12 }}>No table rows available.</p>
      </section>
    );
  }

  const resolvedColumns = columns && columns.length > 0 ? columns : deriveColumns(rows);

  return (
    <section style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 10, background: "#fff" }}>
      {title ? <h5 style={{ margin: "0 0 8px 0", fontSize: 13 }}>{title}</h5> : null}
      <div style={{ overflowX: "auto", maxWidth: "100%" }}>
        <table style={{ borderCollapse: "collapse", minWidth: 500, width: "100%" }}>
          <thead>
            <tr>
              {resolvedColumns.map((column) => (
                <th
                  key={column}
                  style={{
                    borderBottom: "1px solid #cbd5e1",
                    background: "#f8fafc",
                    textAlign: "left",
                    padding: "8px 10px",
                    fontSize: 12,
                    color: "#334155",
                    whiteSpace: "nowrap",
                  }}
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`}>
                {resolvedColumns.map((column) => (
                  <td
                    key={`${rowIndex}-${column}`}
                    style={{
                      borderBottom: "1px solid #f1f5f9",
                      padding: "8px 10px",
                      fontSize: 12,
                      color: "#0f172a",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
