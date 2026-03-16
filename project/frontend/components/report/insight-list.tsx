type InsightListProps = {
  insights: string[];
};

export function InsightList({ insights }: InsightListProps) {
  if (!insights.length) {
    return <p style={{ margin: 0, color: "#6b7280" }}>No insights available.</p>;
  }

  return (
    <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
      {insights.map((insight, index) => (
        <li key={`${insight}-${index}`}>
          <span>{insight}</span>
        </li>
      ))}
    </ul>
  );
}
