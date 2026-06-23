import { apiClient } from "./client";
import { useAuthStore } from "@/lib/store/authStore";
import { clearLastVillageCode } from "@/lib/village/lastVillage";

export async function login(orgId: string, password: string) {
  const { data } = await apiClient.post("/users/login", { org_id: orgId, password });
  return data as { access_token: string; org_name: string; user_name: string };
}

export async function ensureDemoSession() {
  if (typeof window === "undefined") return;
  if (useAuthStore.getState().token) return;
  const { data } = await apiClient.post("/users/demo/token");
  useAuthStore.getState().setAuth(data.access_token, data.scope);
}

export async function getMe() {
  const { data } = await apiClient.get("/users/me");
  return data;
}

export function logout() {
  if (typeof window === "undefined") return;
  useAuthStore.getState().clearAuth();
  clearLastVillageCode();
}
