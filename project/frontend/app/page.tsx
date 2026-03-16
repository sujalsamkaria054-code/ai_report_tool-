import { ChatWindow } from "../components/chat/chat-window";

export default function Page() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)",
        padding: "24px 16px",
      }}
    >
      <ChatWindow />
    </main>
  );
}
