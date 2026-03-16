type InsightListProps = {
  insights: string[];
};

export function InsightList({ insights }: InsightListProps) {
  if (insights.length === 0) {
    return <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>No key insights were returned.</p>;
  }

  return (
    <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
      {insights.map((insight, index) => (
        <li key={`${insight}-${index}`} style={{ fontSize: 13, color: "#1f2937" }}>
          {insight}
        </li>
      ))}
    </ul>
  );
}
