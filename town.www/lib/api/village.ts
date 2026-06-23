import { apiClient } from "./client";
import type { VillageDetail } from "@/lib/types";

export const villageApi = {
  getDetail: async (villageCode: string) => {
    const { data } = await apiClient.get<VillageDetail>(`/village-detail/${villageCode}`);
    return data;
  },
};
