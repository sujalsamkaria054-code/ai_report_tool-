declare const process: { env?: Record<string, string | undefined> } | undefined;

import type { ApiResponse, HealthResponse, QueryRequest, UploadResponse } from "./types";

function resolveApiBaseUrl(): string {
  const envBase = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (envBase) {
    return envBase.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }

  return "http://localhost:8000";
}

const API_BASE_URL = resolveApiBaseUrl();

function normalizeApiResponse(payload: unknown): ApiResponse {
  const raw = (payload ?? {}) as Partial<ApiResponse>;
  return {
    content: typeof raw.content === "string" ? raw.content : "",
    report: raw.report ?? null,
    charts: Array.isArray(raw.charts) ? raw.charts : [],
    tables: Array.isArray(raw.tables) ? raw.tables : [],
    sources: Array.isArray(raw.sources) ? raw.sources.map((s) => String(s)) : [],
    document_id: typeof raw.document_id === "string" ? raw.document_id : null,
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    let detail = "";

    if (contentType.includes("application/json")) {
      try {
        const data = (await response.json()) as { detail?: unknown };
        detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail ?? data);
      } catch {
        detail = await response.text();
      }
    } else {
      detail = await response.text();
    }

    throw new Error(`API ${response.status}: ${detail || response.statusText}`);
  }

  return (await response.json()) as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health", { method: "GET" });
}

export async function queryApi(payload: QueryRequest): Promise<ApiResponse> {
  const response = await request<ApiResponse>("/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return normalizeApiResponse(response);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadResponse>("/upload", {
    method: "POST",
    body: formData,
  });
}
