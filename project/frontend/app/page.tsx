import { ChatWindow } from "../components/chat/chat-window";

export default function Page() {
  return (
    <main style={{ padding: 24 }}>
      <h1>AI Report Tool</h1>
      <p>Upload a document, ask a question, and review structured output.</p>
      <ChatWindow />
    </main>
  );
}
