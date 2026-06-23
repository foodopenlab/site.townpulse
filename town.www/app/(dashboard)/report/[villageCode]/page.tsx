"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import axios from "axios";
import { villageApi } from "@/lib/api/village";
import { reportApi } from "@/lib/api/report";
import { setLastVillageCode } from "@/lib/village/lastVillage";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { formatBudget, formatPercent } from "@/lib/utils/format";
import { dedupePrescriptionsByRank } from "@/lib/utils/prescription";
import type { TviGrade, VillageDetail } from "@/lib/types";

type ReportRisk = {
  vacant_house_rate?: number;
  elderly_rate?: number;
  bus_interval_minutes?: number | null;
  nearest_stop_distance_m?: number | null;
  extinction_probability_5y?: number;
  transport_gap?: boolean;
};

type ReportPrescription = {
  rank: number;
  title: string;
  tvi_gain_min: number;
  tvi_gain_max: number;
  budget_min: number;
  budget_max: number;
};

type ReportBudget = {
  total_min_manwon: number;
  total_max_manwon: number;
  items: { rank: number; title: string; budget_min: number; budget_max: number }[];
};

type ReportData = {
  village_code: string;
  village_name: string;
  sigun_name: string;
  tvi_score: number;
  tvi_grade: TviGrade;
  generated_at: string;
  sections: {
    risk_analysis?: ReportRisk | null;
    prescriptions?: ReportPrescription[] | null;
    budget?: ReportBudget | null;
  };
};

export default function ReportPage({ params }: { params: { villageCode: string } }) {
  const [detail, setDetail] = useState<VillageDetail | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState(false);
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLastVillageCode(params.villageCode);
    villageApi.getDetail(params.villageCode).then(setDetail);
  }, [params.villageCode]);

  const buildReport = async () => {
    setError(null);
    setBuilding(true);
    try {
      const data = await reportApi.build(params.villageCode, {
        include_risk_analysis: true,
        include_prescriptions: true,
        include_budget: true,
        include_map_snapshot: false,
      });
      setReport(data as ReportData);
    } catch (e) {
      const status = axios.isAxiosError(e) ? e.response?.status : undefined;
      if (status === 403) {
        setError("데모 모드에서는 리포트 생성이 제한됩니다. QA 계정으로 로그인해 주세요.");
      } else {
        setError("리포트 데이터를 생성하지 못했습니다. 백엔드(8000) 상태를 확인해 주세요.");
      }
    } finally {
      setBuilding(false);
    }
  };

  const downloadPdf = async () => {
    if (!previewRef.current) return;
    const html2canvas = (await import("html2canvas")).default;
    const { jsPDF } = await import("jspdf");
    const canvas = await html2canvas(previewRef.current, { scale: 2 });
    const img = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");
    const w = pdf.internal.pageSize.getWidth();
    const h = (canvas.height * w) / canvas.width;
    pdf.addImage(img, "PNG", 0, 0, w, h);
    pdf.save(`townpulse-${params.villageCode}.pdf`);
  };

  if (!detail) return <LoadingSpinner />;

  const risk = report?.sections.risk_analysis;
  const prescriptions = dedupePrescriptionsByRank(report?.sections.prescriptions ?? []);
  const budget = report?.sections.budget;
  const budgetItems = budget ? dedupePrescriptionsByRank(budget.items) : [];

  return (
    <div className="space-y-6">
      <nav className="text-sm">
        <Link href={`/map/${detail.village_code}`}>← {detail.village_name}</Link>
      </nav>
      <h1 className="text-2xl font-bold">리포트 생성</h1>
      {error && <ErrorMessage message={error} />}
      <button
        type="button"
        onClick={buildReport}
        disabled={building}
        className="rounded-lg bg-primary px-4 py-2 text-white disabled:opacity-60"
      >
        {building ? "생성 중..." : "리포트 데이터 생성"}
      </button>
      {report && (
        <>
          <div ref={previewRef} className="rounded-xl border border-border bg-card p-6 space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">
                {report.sigun_name} {report.village_name}
              </p>
              <h2 className="text-xl font-bold">마을생존 분석 리포트</h2>
              <p className="text-xs text-muted-foreground">
                TownPulse AI · {new Date(report.generated_at).toLocaleDateString("ko-KR")}
              </p>
            </div>
            <div className="flex items-center gap-2 border-t border-border pt-4">
              <span className="text-lg font-semibold">TVI {report.tvi_score}점</span>
              <Badge grade={report.tvi_grade} />
            </div>
            {risk && (
              <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
                <p>빈집 {formatPercent(risk.vacant_house_rate ?? 0)}</p>
                <p>고령 {formatPercent(risk.elderly_rate ?? 0)}</p>
                <p>배차 {risk.bus_interval_minutes ? `${risk.bus_interval_minutes}분` : "-"}</p>
                <p>5년 소멸확률 {formatPercent(risk.extinction_probability_5y ?? 0)}</p>
              </div>
            )}
            {prescriptions.length > 0 && (
              <div className="space-y-2 border-t border-border pt-4">
                <h3 className="font-semibold">AI 처방 3가지</h3>
                <ul className="space-y-2 text-sm">
                  {prescriptions.map((p) => (
                    <li key={p.rank} className="rounded-lg bg-muted px-3 py-2">
                      <span className="font-medium">
                        {p.rank}순위: {p.title}
                      </span>
                      <p className="text-muted-foreground">
                        TVI +{Number(p.tvi_gain_min).toFixed(1)}~{Number(p.tvi_gain_max).toFixed(1)} ·{" "}
                        {formatBudget(p.budget_min, p.budget_max)}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {budget && (
              <div className="border-t border-border pt-4 text-sm">
                <h3 className="font-semibold">예산 시뮬레이션</h3>
                <p className="mt-1">
                  총 예상 비용:{" "}
                  {formatBudget(
                    budgetItems.reduce((sum, item) => sum + item.budget_min, 0),
                    budgetItems.reduce((sum, item) => sum + item.budget_max, 0),
                  )}
                </p>
              </div>
            )}
          </div>
          <button type="button" onClick={downloadPdf} className="rounded-lg border border-border px-4 py-2">
            PDF 다운로드
          </button>
        </>
      )}
    </div>
  );
}
