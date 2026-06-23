"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { dashboardApi } from "@/lib/api/dashboard";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { TviGrade, VillageListItem } from "@/lib/types";
import {
  getRiskSummary,
  snapFromListItem,
  TVI_GRADE_COLORS,
  TVI_GRADE_LABELS,
} from "@/lib/utils/riskSummary";

const PAGE_SIZE = 5;
const ALL_GRADES: TviGrade[] = ["danger", "warning", "safe"];

type SortOrder = "asc" | "desc";

function FilterChip({
  active,
  label,
  color,
  onClick,
}: {
  active: boolean;
  label: string;
  color?: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
        active
          ? "border-primary bg-primary/10 text-primary"
          : "border-border bg-card text-muted-foreground hover:bg-muted"
      }`}
      style={active && color ? { borderColor: color, color, backgroundColor: `${color}14` } : undefined}
    >
      {label}
    </button>
  );
}

function GradeBadge({ grade }: { grade: TviGrade }) {
  const color = TVI_GRADE_COLORS[grade];
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{ borderColor: color, color, backgroundColor: `${color}14` }}
    >
      <AlertCircle className="h-3 w-3" aria-hidden />
      {TVI_GRADE_LABELS[grade]}
    </span>
  );
}

function ScoreBar({ score, grade }: { score: number; grade: TviGrade }) {
  const color = TVI_GRADE_COLORS[grade];
  const width = Math.max(0, Math.min(100, score));
  return (
    <div className="h-1.5 w-24 overflow-hidden rounded-full bg-muted">
      <div className="h-full rounded-full transition-all" style={{ width: `${width}%`, backgroundColor: color }} />
    </div>
  );
}

export function VillageRiskList() {
  const [villages, setVillages] = useState<VillageListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [grades, setGrades] = useState<Set<TviGrade>>(new Set(ALL_GRADES));
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [page, setPage] = useState(0);

  useEffect(() => {
    dashboardApi
      .getMapVillages()
      .then(setVillages)
      .finally(() => setLoading(false));
  }, []);

  const toggleGrade = (grade: TviGrade) => {
    setGrades((prev) => {
      const next = new Set(prev);
      if (next.has(grade)) next.delete(grade);
      else next.add(grade);
      return next;
    });
    setPage(0);
  };

  const filtered = useMemo(() => {
    return villages
      .filter((v) => grades.has(v.tvi_grade))
      .sort((a, b) => (sortOrder === "asc" ? a.tvi_score - b.tvi_score : b.tvi_score - a.tvi_score));
  }, [villages, grades, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages - 1);
  const pageItems = filtered.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE);

  if (loading) return <LoadingSpinner />;

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">마을 TVI 목록</h2>
        <p className="mt-0.5 text-sm text-muted-foreground">
          TVI 0~100점 · 낮을수록 위험 · 전체 {villages.length}개 마을
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <FilterChip
          active={grades.has("danger")}
          label="위험"
          color={TVI_GRADE_COLORS.danger}
          onClick={() => toggleGrade("danger")}
        />
        <FilterChip
          active={grades.has("warning")}
          label="주의"
          color={TVI_GRADE_COLORS.warning}
          onClick={() => toggleGrade("warning")}
        />
        <FilterChip
          active={grades.has("safe")}
          label="안전"
          color={TVI_GRADE_COLORS.safe}
          onClick={() => toggleGrade("safe")}
        />
        <span className="mx-1 hidden h-4 w-px bg-border sm:inline" aria-hidden />
        <FilterChip
          active={sortOrder === "asc"}
          label="점수 올림차순"
          onClick={() => {
            setSortOrder("asc");
            setPage(0);
          }}
        />
        <FilterChip
          active={sortOrder === "desc"}
          label="점수 내림차순"
          onClick={() => {
            setSortOrder("desc");
            setPage(0);
          }}
        />
      </div>

      {grades.size === 0 ? (
        <p className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
          등급 필터를 하나 이상 선택해 주세요.
        </p>
      ) : (
        <>
          <ul className="space-y-3">
            {pageItems.map((village, index) => {
              const rank = currentPage * PAGE_SIZE + index + 1;
              const summary = getRiskSummary(snapFromListItem(village));
              return (
                <li key={village.village_code}>
                  <Link
                    href={`/map/${village.village_code}`}
                    className="flex items-stretch gap-4 rounded-xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/50"
                  >
                    <span className="w-8 shrink-0 text-2xl font-light text-muted-foreground/60 tabular-nums" aria-hidden>
                      {rank}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold">
                        {village.village_name}{" "}
                        <span className="font-normal text-muted-foreground">({village.sigun_name})</span>
                      </p>
                      <p className="mt-1 truncate text-sm text-muted-foreground">{summary}</p>
                    </div>
                    <div className="flex shrink-0 flex-col items-end justify-between gap-2">
                      <GradeBadge grade={village.tvi_grade} />
                      <div className="text-right">
                        <span className="text-2xl font-bold tabular-nums">{village.tvi_score}</span>
                        <span className="text-sm text-muted-foreground"> / 100</span>
                      </div>
                      <ScoreBar score={village.tvi_score} grade={village.tvi_grade} />
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>

          <div className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 text-sm">
            <span className="text-muted-foreground">
              {filtered.length}개 중 {currentPage * PAGE_SIZE + 1}–
              {Math.min((currentPage + 1) * PAGE_SIZE, filtered.length)}번째
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={currentPage <= 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="rounded-lg border border-border p-1.5 disabled:opacity-40"
                aria-label="이전 페이지"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="min-w-[4.5rem] text-center tabular-nums">
                {currentPage + 1} / {totalPages}
              </span>
              <button
                type="button"
                disabled={currentPage >= totalPages - 1}
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                className="rounded-lg border border-border p-1.5 disabled:opacity-40"
                aria-label="다음 페이지"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
