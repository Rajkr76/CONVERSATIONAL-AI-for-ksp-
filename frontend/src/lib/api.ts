import axios from "axios";
import { getToken } from "./auth";
import { Message, ConversationSummary } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== "undefined") {
        localStorage.removeItem("ksp_auth_token");
        localStorage.removeItem("ksp_auth_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export async function loginApi(username: string, password: string) {
  const response = await api.post("/auth/login", { username, password });
  return response.data;
}

export async function getConversationsApi(): Promise<ConversationSummary[]> {
  const response = await api.get("/history/");
  return response.data;
}

export async function getConversationMessagesApi(id: string): Promise<Message[]> {
  const response = await api.get(`/history/${id}`);
  return response.data;
}

export async function deleteConversationApi(id: string) {
  const response = await api.delete(`/history/${id}`);
  return response.data;
}

export async function streamChatApi(
  question: string,
  conversationId: string | null,
  language: "en" | "kn",
  onChunk: (chunkType: string, data: any) => void,
  onError: (err: any) => void
) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
      language,
    }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("ksp_auth_token");
        localStorage.removeItem("ksp_auth_user");
        window.location.href = "/login";
      }
      return;
    }
    const errorText = await response.text();
    onError(new Error(errorText || "Stream request failed"));
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    // sse-starlette sends \r\n\r\n, some other servers send \n\n
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || "";

    for (const event of events) {
      if (!event.trim()) continue;
      
      const lines = event.split(/\r?\n/);
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const jsonStr = line.slice(6).trim();
            if (jsonStr) {
              const parsed = JSON.parse(jsonStr);
              onChunk(parsed.type, parsed.data);
            }
          } catch (e) {
            console.error("Failed to parse SSE payload", e);
          }
        }
      }
    }
  }
}
