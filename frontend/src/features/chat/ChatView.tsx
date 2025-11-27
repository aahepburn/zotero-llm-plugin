import React from "react";
import { useChatContext } from "../../contexts/ChatContext";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import ErrorBanner from "../../components/feedback/ErrorBanner";

const ChatView: React.FC = () => {
  const { messages, loading, error, sendMessage } = useChatContext();

  return (
    <div className="chat-view">
      <div style={{ padding: "12px 16px" }}>
        <div className="app-heading">Zotero LLM Assistant</div>
        <div className="muted">
          Ask questions over your local library. All processing stays on your machine.
        </div>
        {error && <ErrorBanner message={error} />}
      </div>
      <ChatMessages messages={messages} loading={loading} />
      <ChatInput onSend={sendMessage} disabled={loading} />
    </div>
  );
};

export default ChatView;
