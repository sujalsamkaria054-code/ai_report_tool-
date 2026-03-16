"use client";

import { useState } from "react";

import { queryApi, uploadDocument } from "../../lib/api";
import type { ChatMessage } from "../../lib/types";
import { ChatInput } from "./chat-input";
import { MessageCard } from "./message-card";

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setError(null);
    setIsLoading(true);

    try {
      let currentDocumentId = documentId;

      if (selectedFile) {
        const upload = await uploadDocument(selectedFile);
        currentDocumentId = upload.document_id;
        setDocumentId(upload.document_id);
      }

      const response = await queryApi({
        query: userMessage.content,
        document_id: currentDocumentId,
      });

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.content,
        response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setInput("");
      setSelectedFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process request.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section style={{ maxWidth: 900, margin: "0 auto" }}>
      {messages.map((message) => (
        <MessageCard key={message.id} message={message} />
      ))}

      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      <ChatInput
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        onFileChange={setSelectedFile}
        isLoading={isLoading}
      />
    </section>
  );
}
