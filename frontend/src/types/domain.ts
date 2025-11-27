import type { Citation, Snippet, ChatResponse } from "./api";

export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  citations?: Citation[];
}

export interface ConversationState {
  messages: ChatMessage[];
  lastResponse: ChatResponse | null;
}
