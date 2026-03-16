"use client";

type UploadPanelProps = {
  pendingFile: File | null;
  activeDocument: {
    documentId: string;
    filename: string;
    sizeBytes: number;
    status: string;
  } | null;
  isUploading: boolean;
  onSelectFile: (file: File | null) => void;
  onUpload: () => Promise<void>;
};

function toFileSizeLabel(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadPanel({
  pendingFile,
  activeDocument,
  isUploading,
  onSelectFile,
  onUpload,
}: UploadPanelProps) {
  const hasPending = Boolean(pendingFile);

  return (
    <aside
      style={{
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        borderRadius: 16,
        padding: 16,
        display: "grid",
        gap: 14,
        boxShadow: "0 6px 18px rgba(15,23,42,0.06)",
      }}
    >
      <div>
        <h2 style={{ margin: 0, fontSize: 16 }}>Document Session</h2>
        <p style={{ margin: "6px 0 0", color: "#64748b", fontSize: 13 }}>
          Upload one document to make your chat context-aware.
        </p>
      </div>

      <label
        style={{
          border: "1px dashed #94a3b8",
          borderRadius: 12,
          padding: 12,
          display: "grid",
          gap: 8,
          cursor: "pointer",
          background: "#f8fafc",
        }}
      >
        <strong style={{ fontSize: 13 }}>Drop a file or click to browse</strong>
        <span style={{ color: "#64748b", fontSize: 12 }}>PDF, TXT, CSV</span>
        <input
          type="file"
          accept=".pdf,.txt,.csv"
          onChange={(event) => onSelectFile(event.target.files?.[0] ?? null)}
          style={{ display: "none" }}
          disabled={isUploading}
        />
      </label>

      {hasPending && pendingFile ? (
        <div
          style={{
            border: "1px solid #e2e8f0",
            borderRadius: 10,
            padding: 10,
            background: "#ffffff",
          }}
        >
          <div style={{ fontWeight: 600, fontSize: 13 }}>{pendingFile.name}</div>
          <div style={{ color: "#64748b", fontSize: 12 }}>{toFileSizeLabel(pendingFile.size)}</div>
          <button
            onClick={onUpload}
            disabled={isUploading}
            style={{
              marginTop: 10,
              width: "100%",
              border: 0,
              borderRadius: 8,
              background: "#1d4ed8",
              color: "#fff",
              padding: "8px 10px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {isUploading ? "Uploading..." : "Upload Document"}
          </button>
        </div>
      ) : null}

      <div
        style={{
          border: "1px solid #e2e8f0",
          borderRadius: 10,
          padding: 10,
          background: activeDocument ? "#ecfeff" : "#f8fafc",
        }}
      >
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase" }}>Active Document</div>
        {activeDocument ? (
          <>
            <div style={{ fontWeight: 600, marginTop: 6, fontSize: 13 }}>{activeDocument.filename}</div>
            <div style={{ color: "#334155", fontSize: 12, marginTop: 4 }}>Status: {activeDocument.status}</div>
            <div style={{ color: "#334155", fontSize: 12 }}>ID: {activeDocument.documentId.slice(0, 12)}...</div>
          </>
        ) : (
          <p style={{ margin: "6px 0 0", color: "#64748b", fontSize: 13 }}>
            No document uploaded yet. You can still ask general questions.
          </p>
        )}
      </div>
    </aside>
  );
}
