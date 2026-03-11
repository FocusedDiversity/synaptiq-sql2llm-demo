import type { QueryResponse, SuggestionCategory, SchemaTable } from "../types";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body.error) message = body.error;
      if (body.detail) message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      // use default message
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export async function submitQuery(query: string): Promise<QueryResponse> {
  return request<QueryResponse>("/api/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function fetchSuggestions(): Promise<SuggestionCategory[]> {
  return request<SuggestionCategory[]>("/api/suggestions");
}

export async function fetchSchema(): Promise<SchemaTable[]> {
  return request<SchemaTable[]>("/api/schema");
}
