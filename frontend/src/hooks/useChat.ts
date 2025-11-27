import { useState } from "react";
import { chat as chatApi } from "../api/chat";
import type { ChatMessage } from "../types/domain";
import type { ChatResponse } from "../types/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  async function sendMessage(content: string) {
    if (!content.trim() || loading) return;
    setError(null);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: content.trim(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await chatApi({ query: content.trim() });
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.summary,
        citations: res.citations,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setLastResponse(res);
    } catch (e: any) {
      setError(e.message ?? "Failed to get answer");
    } finally {
      setLoading(false);
    }
  }

  function loadThread(thread: { id: string; title?: string; messages: ChatMessage[]; lastResponse?: ChatResponse }) {
    if (!thread) return;
    setMessages(thread.messages || []);
    if (thread.lastResponse) setLastResponse(thread.lastResponse);
  }

  return { messages, loading, error, lastResponse, sendMessage, loadThread };
}
