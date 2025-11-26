// src/backendClient.ts

export interface ChatSnippet {
  snippet: string;
  item_id: string;
  title?: string;
  year?: string;
}

export interface ChatCitation {
  item_id: string;
  title: string;
  year?: string;
}

export interface ChatResponse {
  summary: string;
  citations: ChatCitation[];
  snippets: ChatSnippet[];
}

const BASE_URL = "http://127.0.0.1:8000"; // TODO: make configurable

async function handleJSONResponse<T>(resp: Response): Promise<T> {
  const text = await resp.text();
  if (!resp.ok) {
    throw new Error(`Backend error ${resp.status}: ${text}`);
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error("Backend returned invalid JSON");
  }
}

export async function pingBackend(): Promise<boolean> {
  try {
    const resp = await fetch(`${BASE_URL}/health`, { method: "GET" });
    return resp.ok;
  } catch {
    return false;
  }
}

export async function indexLibrary(): Promise<void> {
  const resp = await fetch(`${BASE_URL}/index_library`, {
    method: "POST",
  });
  await handleJSONResponse<unknown>(resp);
}

export async function chat(
  question: string,
  itemIds?: string[],
): Promise<ChatResponse> {
  const params = new URLSearchParams();
  params.set("query", question);
  if (itemIds && itemIds.length) {
    params.set("item_ids", itemIds.join(","));
  }

  const resp = await fetch(`${BASE_URL}/chat?${params.toString()}`, {
    method: "GET",
  });
  return handleJSONResponse<ChatResponse>(resp);
}
