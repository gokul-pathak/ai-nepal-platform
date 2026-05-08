export type Tool = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ToolRunRequest = {
  input: string;
  language: string;
};

export type ToolRunResponse = {
  tool: string;
  result: string;
  usage: {
    remaining_daily_requests: number;
  };
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const SESSION_KEY = "ai_nepal_session_id";

function buildUrl(path: string): string {
  return `${API_BASE_URL.replace(/\/$/, "")}${path}`;
}

export async function getTools(): Promise<Tool[]> {
  const response = await fetch(buildUrl("/api/v1/tools"), { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load tools");
  }
  return response.json() as Promise<Tool[]>;
}

export function getSessionId(): string {
  if (typeof window === "undefined") {
    return "";
  }

  const existing = window.localStorage.getItem(SESSION_KEY);
  if (existing) {
    return existing;
  }

  const newId = `sess_${crypto.randomUUID()}`;
  window.localStorage.setItem(SESSION_KEY, newId);
  return newId;
}

export async function runTool(slug: string, payload: ToolRunRequest): Promise<ToolRunResponse> {
  const sessionId = getSessionId();
  const response = await fetch(buildUrl(`/api/v1/tools/${slug}/run`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionId,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      detail = "Request failed";
    }

    const err = new Error(detail);
    (err as Error & { status?: number }).status = response.status;
    throw err;
  }

  return response.json() as Promise<ToolRunResponse>;
}
