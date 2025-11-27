import React, { useState } from "react";

interface Props {
  onSend: (content: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<Props> = ({ onSend, disabled }) => {
  const [value, setValue] = useState("");

  function submit() {
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="chat-view__input">
      <div className="chat-input__wrapper">
        <textarea
          className="chat-input__textarea"
          placeholder="Ask a question about your Zotero library…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <button className="btn" onClick={submit} disabled={disabled}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
