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
      <section>
        {title ? <h5 style={{ margin: "0 0 6px 0" }}>{title}</h5> : null}
        <p style={{ margin: 0, color: "#6b7280" }}>No table rows available.</p>
      </section>
    );
  }

  const resolvedColumns = columns && columns.length > 0 ? columns : deriveColumns(rows);

  return (
    <section>
      {title ? <h5 style={{ margin: "0 0 6px 0" }}>{title}</h5> : null}
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              {resolvedColumns.map((column) => (
                <th
                  key={column}
                  style={{
                    border: "1px solid #d1d5db",
                    background: "#f9fafb",
                    textAlign: "left",
                    padding: "6px 8px",
                    fontSize: 12,
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
                    style={{ border: "1px solid #e5e7eb", padding: "6px 8px", fontSize: 12 }}
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
