"use client";

type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  hasActiveDocument: boolean;
};

export function ChatInput({
  value,
  onChange,
  onSubmit,
  isLoading,
  hasActiveDocument,
}: ChatInputProps) {
  return (
    <div
      style={{
        position: "sticky",
        bottom: 0,
        background: "rgba(248,250,252,0.95)",
        backdropFilter: "blur(4px)",
        borderTop: "1px solid #e2e8f0",
        padding: 12,
        display: "grid",
        gap: 10,
      }}
    >
      <div style={{ fontSize: 12, color: "#64748b" }}>
        {hasActiveDocument
          ? "Document-aware mode enabled. Ask questions about your uploaded file."
          : "No active document. Upload a file for document-aware answers."}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 10, alignItems: "end" }}>
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Ask a question about the document..."
          rows={3}
          disabled={isLoading}
          style={{
            width: "100%",
            resize: "none",
            borderRadius: 10,
            border: "1px solid #cbd5e1",
            padding: 10,
            fontSize: 14,
            lineHeight: 1.4,
          }}
        />
        <button
          onClick={onSubmit}
          disabled={isLoading || !value.trim()}
          style={{
            border: 0,
            borderRadius: 10,
            background: isLoading || !value.trim() ? "#94a3b8" : "#0f172a",
            color: "#fff",
            padding: "10px 16px",
            fontWeight: 600,
            cursor: isLoading || !value.trim() ? "not-allowed" : "pointer",
            height: 42,
          }}
        >
          {isLoading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
