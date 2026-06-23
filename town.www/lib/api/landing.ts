import axios from "axios";
import type { DashboardSummary } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/** 랜딩 통계 — 토큰을 localStorage에 저장하지 않고 1회 조회 */
export async function fetchLandingStats(): Promise<Pick<
  DashboardSummary,
  "danger_count" | "total_villages" | "transport_gap_count"
> | null> {
  try {
    const { data: tokenRes } = await axios.post<{ access_token: string }>(
      `${API_BASE}/api/townpulse/users/demo/token`,
    );
    const { data } = await axios.get<DashboardSummary>(`${API_BASE}/api/townpulse/dashboard/summary`, {
      headers: { Authorization: `Bearer ${tokenRes.access_token}` },
    });
    return {
      danger_count: data.danger_count,
      total_villages: data.total_villages,
      transport_gap_count: data.transport_gap_count,
    };
  } catch {
    return null;
  }
}
