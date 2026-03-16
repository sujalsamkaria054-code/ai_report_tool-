type RecommendationListProps = {
  recommendations: string[];
};

export function RecommendationList({ recommendations }: RecommendationListProps) {
  if (recommendations.length === 0) {
    return <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>No recommendations were returned.</p>;
  }

  return (
    <ol style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
      {recommendations.map((item, index) => (
        <li key={`${item}-${index}`} style={{ fontSize: 13, color: "#1f2937" }}>
          {item}
        </li>
      ))}
    </ol>
  );
}
