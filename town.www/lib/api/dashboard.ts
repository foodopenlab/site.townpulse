import { apiClient } from "./client";
import type { DashboardSummary, VillageListItem, VillageMapSummary } from "@/lib/types";

export const dashboardApi = {
  getSummary: async () => {
    const { data } = await apiClient.get<DashboardSummary>("/dashboard/summary");
    return data;
  },
  getMapVillages: async (params?: { grade?: string; sigun?: string }) => {
    const { data } = await apiClient.get<VillageListItem[]>("/dashboard/map/villages", { params });
    return data;
  },
  getMapVillageSummary: async (villageCode: string) => {
    const { data } = await apiClient.get<VillageMapSummary>(`/dashboard/map/villages/${villageCode}`);
    return data;
  },
};
