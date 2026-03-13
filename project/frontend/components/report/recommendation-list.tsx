type RecommendationListProps = {
  recommendations: string[];
};

export function RecommendationList({ recommendations }: RecommendationListProps) {
  if (!recommendations.length) {
    return <p style={{ margin: 0, color: "#6b7280" }}>No recommendations available.</p>;
  }

  return (
    <ol style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
      {recommendations.map((recommendation, index) => (
        <li key={`${recommendation}-${index}`}>{recommendation}</li>
      ))}
    </ol>
  );
}
