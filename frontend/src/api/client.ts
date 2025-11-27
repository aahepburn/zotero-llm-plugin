const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path.startsWith("/") ? path : `/${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed: ${res.status} ${text}`);
  }

  return (await res.json()) as T;
}

export { BASE_URL, request };
