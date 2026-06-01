// Centralized, typed API client. Calls are relative ("/api/...") so the same
// build works in dev (Vite proxy) and prod (nginx proxy).

export interface TraceEntry {
  tool: string;
  args: Record<string, unknown>;
  result: string;
}

export interface ChatResponse {
  reply: string;
  trace: TraceEntry[];
  session_id: string;
}

export interface MenuResponse {
  today: string;
  menu: Record<string, Record<string, string[]>>;
}

export interface RatingSummaryItem {
  dish: string;
  count: number;
  average: number;
  last_rated: string;
}

export interface RatingSummaryResponse {
  items: RatingSummaryItem[];
  total_ratings: number;
}

export interface HealthResponse {
  status: string;
  ollama_reachable: boolean;
  model_present: boolean;
  model: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep the generic message
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export function sendChat(message: string, sessionId: string | null): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

export type StreamEvent =
  | { type: "session"; session_id: string }
  | { type: "tool"; tool: string; args: Record<string, unknown>; result: string }
  | { type: "token"; text: string }
  | { type: "done" }
  | { type: "error"; detail: string };

// Streams the agent reply via SSE so tokens render as they're generated.
export async function streamChat(
  message: string,
  sessionId: string | null,
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Stream failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      const line = frame.trim();
      if (!line.startsWith("data:")) continue;
      try {
        onEvent(JSON.parse(line.slice(5).trim()) as StreamEvent);
      } catch {
        // ignore malformed frame
      }
    }
  }
}

export function getMenu(): Promise<MenuResponse> {
  return request<MenuResponse>("/api/menu");
}

export function getRatingsSummary(): Promise<RatingSummaryResponse> {
  return request<RatingSummaryResponse>("/api/ratings/summary");
}

export function submitRating(dish: string, rating: number): Promise<unknown> {
  return request("/api/ratings", {
    method: "POST",
    body: JSON.stringify({ dish, rating }),
  });
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}
