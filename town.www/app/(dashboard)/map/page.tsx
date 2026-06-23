"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { dashboardApi } from "@/lib/api/dashboard";
import { setLastVillageCode } from "@/lib/village/lastVillage";
import { useMapStore } from "@/lib/store/mapStore";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { MapFilters } from "@/components/map/MapFilters";
import { VillageSummaryCard } from "@/components/map/VillageSummaryCard";
import type { VillageListItem, VillageMapSummary } from "@/lib/types";

const VillageMap = dynamic(() => import("@/components/map/VillageMap").then((m) => m.VillageMap), {
  ssr: false,
  loading: () => <LoadingSpinner />,
});

export default function MapPage() {
  const { grade, sigun, indicator, setGrade, setSigun, setIndicator } = useMapStore();
  const [villages, setVillages] = useState<VillageListItem[]>([]);
  const [selected, setSelected] = useState<VillageMapSummary | null>(null);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);

  useEffect(() => {
    const params: { grade?: string; sigun?: string } = {};
    if (grade) params.grade = grade;
    if (sigun) params.sigun = sigun;
    dashboardApi.getMapVillages(params).then(setVillages);
  }, [grade, sigun]);

  const onSelect = async (code: string) => {
    setLastVillageCode(code);
    setSelectedCode(code);
    const summary = await dashboardApi.getMapVillageSummary(code);
    setSelected(summary);
  };

  const markers = useMemo(() => villages, [villages]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="text-2xl font-bold">소멸위험 지도</h1>
        <MapFilters
          grade={grade}
          sigun={sigun}
          indicator={indicator}
          onGradeChange={setGrade}
          onSigunChange={setSigun}
          onIndicatorChange={setIndicator}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <VillageMap
            villages={markers}
            onSelect={onSelect}
            selectedCode={selectedCode}
            indicator={indicator}
          />
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          {selected ? (
            <VillageSummaryCard selected={selected} />
          ) : (
            <p className="text-sm text-muted-foreground">지도에서 마을을 선택하세요.</p>
          )}
        </div>
      </div>
    </div>
  );
}
