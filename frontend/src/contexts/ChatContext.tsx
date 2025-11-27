import React, { createContext, useContext } from "react";
import type { ChatResponse } from "../types/api";
import type { ChatMessage } from "../types/domain";
import { useChat as useChatHook } from "../hooks/useChat";

type ChatContextShape = {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  lastResponse: ChatResponse | null;
  sendMessage: (content: string) => Promise<void>;
  loadThread: (thread: { id: string; title?: string; messages: ChatMessage[]; lastResponse?: ChatResponse }) => void;
};

const ChatContext = createContext<ChatContextShape | null>(null);

export const ChatProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const { messages, loading, error, lastResponse, sendMessage, loadThread } = useChatHook();
  return (
    <ChatContext.Provider value={{ messages, loading, error, lastResponse, sendMessage, loadThread }}>
      {children}
    </ChatContext.Provider>
  );
};

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatContext must be used within ChatProvider");
  return ctx;
}

export default ChatContext;
