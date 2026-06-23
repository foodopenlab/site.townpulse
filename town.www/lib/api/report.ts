import { apiClient } from "./client";

export const reportApi = {
  build: async (villageCode: string, body: Record<string, boolean>) => {
    const { data } = await apiClient.post(`/report-data/${villageCode}`, body);
    return data;
  },
};
