"use client";

import { useMemo, useState } from "react";

import { queryApi, uploadDocument } from "../../lib/api";
import type { ChatMessage } from "../../lib/types";
import { ChatInput } from "./chat-input";
import { MessageCard } from "./message-card";
import { UploadPanel } from "./upload-panel";

type ActiveDocument = {
  documentId: string;
  filename: string;
  sizeBytes: number;
  status: string;
};

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [activeDocument, setActiveDocument] = useState<ActiveDocument | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  const hasMessages = messages.length > 0;

  const headerSubtitle = useMemo(() => {
    if (activeDocument) {
      return `Active: ${activeDocument.filename}`;
    }
    return "Upload a document to start document-aware chat.";
  }, [activeDocument]);

  const handleUpload = async () => {
    if (!pendingFile || isUploading) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const upload = await uploadDocument(pendingFile);
      setActiveDocument({
        documentId: upload.document_id,
        filename: upload.filename,
        sizeBytes: upload.size_bytes,
        status: upload.status,
      });
      setPendingFile(null);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQueryError(null);
    setIsLoading(true);

    try {
      const response = await queryApi({
        query: userMessage.content,
        document_id: activeDocument?.documentId,
      });

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.content,
        response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setInput("");
    } catch (err) {
      setQueryError(err instanceof Error ? err.message : "Failed to process request.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section
      style={{
        maxWidth: 1280,
        margin: "0 auto",
        display: "grid",
        gridTemplateColumns: "300px minmax(0, 1fr)",
        gap: 16,
      }}
    >
      <UploadPanel
        pendingFile={pendingFile}
        activeDocument={activeDocument}
        isUploading={isUploading}
        onSelectFile={setPendingFile}
        onUpload={handleUpload}
        uploadError={uploadError}
      />

      <div
        style={{
          display: "grid",
          gridTemplateRows: "auto 1fr auto",
          background: "#f8fafc",
          border: "1px solid #e2e8f0",
          borderRadius: 16,
          minHeight: "calc(100vh - 48px)",
          overflow: "hidden",
        }}
      >
        <header
          style={{
            padding: "14px 16px",
            borderBottom: "1px solid #e2e8f0",
            background: "#ffffff",
          }}
        >
          <h1 style={{ margin: 0, fontSize: 18 }}>AI Report Assistant</h1>
          <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: 13 }}>{headerSubtitle}</p>
        </header>

        <div style={{ overflowY: "auto", padding: 16, display: "grid", gap: 12, alignContent: "start" }}>
          {!hasMessages ? (
            <div
              style={{
                border: "1px dashed #cbd5e1",
                borderRadius: 12,
                padding: 18,
                color: "#475569",
                background: "#ffffff",
              }}
            >
              <strong>Start a conversation</strong>
              <p style={{ margin: "8px 0 0" }}>
                Upload a document from the left panel, then ask questions to get report cards, charts, tables, and
                sources in your chat.
              </p>
            </div>
          ) : (
            messages.map((message) => <MessageCard key={message.id} message={message} />)
          )}

          {isLoading ? (
            <div
              style={{
                border: "1px solid #e2e8f0",
                background: "#ffffff",
                borderRadius: 12,
                padding: 12,
                color: "#64748b",
                fontSize: 13,
              }}
            >
              Assistant is analyzing your request...
            </div>
          ) : null}

          {queryError ? (
            <div
              style={{
                border: "1px solid #fecaca",
                background: "#fef2f2",
                color: "#991b1b",
                borderRadius: 10,
                padding: "10px 12px",
                fontSize: 13,
              }}
            >
              {queryError}
            </div>
          ) : null}
        </div>

        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          hasActiveDocument={Boolean(activeDocument)}
        />
      </div>
    </section>
  );
}
