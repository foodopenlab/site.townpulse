"use client";

import { useEffect, useState } from "react";
import { fetchLandingStats } from "@/lib/api/landing";

const FALLBACK = { danger_count: 72, total_villages: 228, transport_gap_count: 44 };

export function StatsSection() {
  const [stats, setStats] = useState(FALLBACK);

  useEffect(() => {
    fetchLandingStats().then((data) => {
      if (data) setStats(data);
    });
  }, []);

  const items = [
    { value: stats.danger_count, label: "소멸위험 마을", sub: "danger 등급", danger: true },
    { value: stats.total_villages, label: "충북 전체", sub: "읍면동 분석", danger: false },
    { value: stats.transport_gap_count, label: "교통 공백", sub: "마을 수", danger: false },
  ];

  return (
    <div className="mx-auto grid max-w-2xl grid-cols-3 gap-3 px-4 pb-12 md:px-8">
      {items.map((item) => (
        <div key={item.label} className="rounded-xl border border-border bg-card p-4 text-center shadow-sm">
          <p className={`text-2xl font-bold tabular-nums ${item.danger ? "text-danger" : ""}`}>{item.value}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {item.label}
            <br />
            {item.sub}
          </p>
        </div>
      ))}
    </div>
  );
}
