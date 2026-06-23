import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/townpulse`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("townpulse_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      const path = err.config?.url ?? "";
      // 로그인 실패 401은 여기서 리다이렉트하지 않음 (폼에서 에러 표시)
      if (!path.includes("/users/login")) {
        localStorage.removeItem("townpulse_token");
        localStorage.removeItem("townpulse_scope");
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  },
);
