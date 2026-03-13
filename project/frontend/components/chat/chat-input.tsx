"use client";

type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onFileChange: (file: File | null) => void;
  isLoading: boolean;
};

export function ChatInput({
  value,
  onChange,
  onSubmit,
  onFileChange,
  isLoading,
}: ChatInputProps) {
  return (
    <div style={{ display: "grid", gap: 8 }}>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask a question about your uploaded file"
        rows={3}
        disabled={isLoading}
      />

      <input
        type="file"
        accept=".pdf,.txt,.csv"
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        disabled={isLoading}
      />

      <button onClick={onSubmit} disabled={isLoading || !value.trim()}>
        {isLoading ? "Thinking..." : "Send"}
      </button>
    </div>
  );
}
