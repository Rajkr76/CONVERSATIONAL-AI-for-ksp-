import { create } from "zustand";
import { Message, ConversationSummary } from "@/types";
import { streamChatApi, getConversationsApi, getConversationMessagesApi, deleteConversationApi } from "@/lib/api";

interface ChatState {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  language: "en" | "kn";
  statusText: string | null;

  setLanguage: (lang: "en" | "kn") => void;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  newChat: () => void;
  deleteConversation: (id: string) => Promise<void>;
  sendMessage: (question: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  language: "en",
  statusText: null,

  setLanguage: (lang) => set({ language: lang }),

  loadConversations: async () => {
    try {
      const conversations = await getConversationsApi();
      set({ conversations });
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  },

  selectConversation: async (id: string) => {
    try {
      const messages = await getConversationMessagesApi(id);
      set({ currentConversationId: id, messages });
    } catch (err) {
      console.error("Failed to load conversation messages", err);
    }
  },

  newChat: () => {
    set({ currentConversationId: null, messages: [], statusText: null });
  },

  deleteConversation: async (id: string) => {
    try {
      await deleteConversationApi(id);
      const conversations = get().conversations.filter(c => c.conversation_id !== id);
      const isCurrent = get().currentConversationId === id;
      set({
        conversations,
        ...(isCurrent ? { currentConversationId: null, messages: [] } : {}),
      });
    } catch (err) {
      console.error("Failed to delete conversation", err);
    }
  },

  sendMessage: async (question: string) => {
    if (!question.trim() || get().isStreaming) return;

    const userMsgId = `user_${Date.now()}`;
    const assistantMsgId = `assistant_${Date.now()}`;

    const userMessage: Message = {
      id: userMsgId,
      role: "user",
      content: question,
      language: get().language,
      created_at: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      isStreaming: true,
      language: get().language,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage, assistantMessage],
      isStreaming: true,
      statusText: "Initializing query pipeline...",
    }));

    await streamChatApi(
      question,
      get().currentConversationId,
      get().language,
      (type, data) => {
        if (type === "status") {
          set({ statusText: data.message });
        } else if (type === "sql") {
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    sql_query: data.query,
                    sql_result: {
                      query: data.query,
                      columns: data.columns,
                      rows: data.rows,
                      row_count: data.row_count,
                      execution_time_ms: data.execution_time_ms,
                    },
                  }
                : m
            ),
          }));
        } else if (type === "token") {
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? { ...m, content: m.content + data.content }
                : m
            ),
          }));
        } else if (type === "chart") {
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, chart_data: data } : m
            ),
          }));
        } else if (type === "graph") {
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, graph_data: data } : m
            ),
          }));
        } else if (type === "meta") {
          set((state) => ({
            currentConversationId: data.conversation_id,
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    confidence: data.confidence,
                    evidence_refs: data.evidence_refs,
                    suggested_questions: data.suggested_questions,
                  }
                : m
            ),
          }));
        } else if (type === "done") {
          set((state) => ({
            isStreaming: false,
            statusText: null,
            messages: state.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, isStreaming: false } : m
            ),
          }));
          get().loadConversations();
        } else if (type === "error") {
          set((state) => ({
            isStreaming: false,
            statusText: null,
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    content: m.content + `\n\n⚠️ ${data.message}`,
                    isStreaming: false,
                  }
                : m
            ),
          }));
        }
      },
      (err) => {
        console.error("Stream error", err);
        set((state) => ({
          isStreaming: false,
          statusText: null,
          messages: state.messages.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  content: m.content || "⚠️ Failed to connect to AI pipeline server.",
                  isStreaming: false,
                }
              : m
          ),
        }));
      }
    );
  },
}));
