"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { villageApi } from "@/lib/api/village";
import { setLastVillageCode } from "@/lib/village/lastVillage";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { IndicatorCards, TransportBadges } from "@/components/village/IndicatorCards";
import { formatPercent } from "@/lib/utils/format";
import type { VillageDetail } from "@/lib/types";

export default function VillageDetailPage({ params }: { params: { villageCode: string } }) {
  const [detail, setDetail] = useState<VillageDetail | null>(null);

  useEffect(() => {
    setLastVillageCode(params.villageCode);
    villageApi.getDetail(params.villageCode).then(setDetail);
  }, [params.villageCode]);

  if (!detail) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <nav className="text-sm text-muted-foreground">
        <Link href="/map">지도</Link> / {detail.village_name}
      </nav>
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold">{detail.village_name}</h1>
        <Badge grade={detail.tvi_grade} />
        <span className="font-mono">TVI {detail.tvi_score}</span>
        <TransportBadges detail={detail} />
      </div>
      <IndicatorCards detail={detail} />
      <div className="rounded-lg border border-border bg-card p-4">
        <p>5년 소멸 확률: {formatPercent(detail.extinction_probability_5y)}</p>
      </div>
      <div className="flex gap-3">
        <Link
          href={`/prescription/${detail.village_code}`}
          className="rounded-lg bg-primary px-4 py-2 text-white"
        >
          AI 처방 보기
        </Link>
        <Link href={`/report/${detail.village_code}`} className="rounded-lg border border-border px-4 py-2">
          리포트 생성
        </Link>
      </div>
    </div>
  );
}
