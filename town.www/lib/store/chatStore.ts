import { create } from "zustand";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type ChatState = {
  messages: ChatMessage[];
  streaming: boolean;
  appendUser: (content: string) => void;
  startAssistant: () => string;
  appendToLastAssistant: (chunk: string) => void;
  finishAssistant: () => void;
  reset: () => void;
};

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  streaming: false,
  appendUser: (content) =>
    set((s) => ({
      messages: [...s.messages, { id: `u-${Date.now()}`, role: "user", content }],
    })),
  startAssistant: () => {
    const id = `a-${Date.now()}`;
    set((s) => ({
      streaming: true,
      messages: [...s.messages, { id, role: "assistant", content: "" }],
    }));
    return id;
  },
  appendToLastAssistant: (chunk) =>
    set((s) => {
      if (!s.messages.length) return s;
      const next = [...s.messages];
      const last = next[next.length - 1];
      if (last.role !== "assistant") return s;
      next[next.length - 1] = { ...last, content: last.content + chunk };
      return { messages: next };
    }),
  finishAssistant: () => set({ streaming: false }),
  reset: () => set({ messages: [], streaming: false }),
}));
