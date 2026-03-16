type SourceListProps = {
  sources: string[];
};

export function SourceList({ sources }: SourceListProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <section style={{ display: "grid", gap: 6 }}>
      <h4 style={{ margin: 0, fontSize: 13, color: "#334155" }}>Sources</h4>
      <ul style={{ margin: 0, paddingLeft: 18, color: "#475569", fontSize: 12 }}>
        {sources.map((source) => (
          <li key={source} style={{ overflowWrap: "anywhere" }}>
            {source}
          </li>
        ))}
      </ul>
    </section>
  );
}
