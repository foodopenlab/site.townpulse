import { apiClient } from "./client";
import type { PrescriptionList } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const prescriptionApi = {
  getByVillage: async (villageId: string) => {
    const { data } = await apiClient.get<PrescriptionList>(`/prescription-results/by-village/${villageId}`);
    return data;
  },
  create: async (villageId: string) => {
    const { data } = await apiClient.post("/prescription-results", { village_id: villageId });
    return data;
  },
  streamUrl: (prescriptionId: string, token: string) =>
    `${API_BASE}/api/townpulse/prescription-results/${prescriptionId}/stream?token=${encodeURIComponent(token)}`,
};
