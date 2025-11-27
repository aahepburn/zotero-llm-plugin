import React from "react";
import type { ChatMessage } from "../../types/domain";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
}

const ChatMessages: React.FC<Props> = ({ messages, loading }) => {
  return (
    <div className="chat-view__messages">
      <div className="message-list">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`message message--${m.role === "user" ? "user" : "assistant"}`}
          >
            <div className="message__role">
              {m.role === "user" ? "You" : "Assistant"}
            </div>
            <div>{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message message--assistant">
            <div className="message__role">Assistant</div>
            <div>Thinking…</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessages;
