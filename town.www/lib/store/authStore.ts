import { create } from "zustand";

type AuthState = {
  token: string | null;
  scope: string | null;
  setAuth: (token: string, scope?: string | null) => void;
  clearAuth: () => void;
  hydrate: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  scope: null,
  setAuth: (token, scope = null) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("townpulse_token", token);
      if (scope) localStorage.setItem("townpulse_scope", scope);
      else localStorage.removeItem("townpulse_scope");
    }
    set({ token, scope });
  },
  clearAuth: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("townpulse_token");
      localStorage.removeItem("townpulse_scope");
    }
    set({ token: null, scope: null });
  },
  hydrate: () => {
    if (typeof window === "undefined") return;
    set({
      token: localStorage.getItem("townpulse_token"),
      scope: localStorage.getItem("townpulse_scope"),
    });
  },
}));
