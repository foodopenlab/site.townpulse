"use client";

import { useEffect, useState } from "react";
import { dashboardApi } from "@/lib/api/dashboard";
import { VillageRiskList } from "@/components/dashboard/VillageRiskList";
import { StatCard } from "@/components/dashboard/StatCard";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import type { DashboardSummary } from "@/lib/types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dashboardApi
      .getSummary()
      .then(setData)
      .catch(() =>
        setError("대시보드 데이터를 불러오지 못했습니다. 백엔드(8000)를 재시작한 뒤 다시 시도해 주세요."),
      );
  }, []);

  if (error) return <ErrorMessage message={error} />;
  if (!data) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">충북 마을생존 대시보드</h1>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard title="전체 마을" value={data.total_villages} />
        <StatCard title="소멸위험" value={data.danger_count} subtitle="위험 등급" />
        <StatCard title="주의" value={data.warning_count} subtitle="주의 등급" />
        <StatCard title="교통 공백" value={data.transport_gap_count} subtitle="버스 접근 불가" />
      </div>
      <VillageRiskList />
    </div>
  );
}
