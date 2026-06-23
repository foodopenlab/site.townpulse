import Link from "next/link";
import { AlertCircle } from "lucide-react";
import type { DangerVillageItem } from "@/lib/types";
import { getRiskSummary, gradeFromScore, TVI_GRADE_COLORS, TVI_GRADE_LABELS } from "@/lib/utils/riskSummary";

function GradeBadge({ grade }: { grade: DangerVillageItem["tvi_grade"] }) {
  const g = grade ?? "warning";
  const color = TVI_GRADE_COLORS[g];
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{ borderColor: color, color, backgroundColor: `${color}14` }}
    >
      <AlertCircle className="h-3 w-3" aria-hidden />
      {TVI_GRADE_LABELS[g]}
    </span>
  );
}

function ScoreBar({ score, grade }: { score: number; grade: DangerVillageItem["tvi_grade"] }) {
  const g = grade ?? "warning";
  const color = TVI_GRADE_COLORS[g];
  const width = Math.max(0, Math.min(100, score));

  return (
    <div className="h-1.5 w-24 overflow-hidden rounded-full bg-muted">
      <div className="h-full rounded-full transition-all" style={{ width: `${width}%`, backgroundColor: color }} />
    </div>
  );
}

export function DangerTop5({ villages }: { villages: DangerVillageItem[] }) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">위험 마을 TOP 5</h2>
        <p className="mt-0.5 text-sm text-muted-foreground">TVI 0~100점 · 낮을수록 위험</p>
        <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-danger" />
            위험 (0–30)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-warning" />
            주의 (31–60)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-safe" />
            안전 (61–100)
          </span>
        </div>
      </div>

      <ul className="space-y-3">
        {villages.map((village, index) => {
          const grade = village.tvi_grade ?? gradeFromScore(village.tvi_score);
          const summary = getRiskSummary(village);
          return (
            <li key={village.village_code}>
              <Link
                href={`/map/${village.village_code}`}
                className="flex items-stretch gap-4 rounded-xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/50"
              >
                <span className="w-6 shrink-0 text-2xl font-light text-muted-foreground/60" aria-hidden>
                  {index + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <p className="font-semibold">
                    {village.village_name}{" "}
                    <span className="font-normal text-muted-foreground">({village.sigun_name})</span>
                  </p>
                  <p className="mt-1 truncate text-sm text-muted-foreground">{summary}</p>
                </div>

                <div className="flex shrink-0 flex-col items-end justify-between gap-2">
                  <GradeBadge grade={grade} />
                  <div className="text-right">
                    <span className="text-2xl font-bold tabular-nums">{village.tvi_score}</span>
                    <span className="text-sm text-muted-foreground"> / 100</span>
                  </div>
                  <ScoreBar score={village.tvi_score} grade={grade} />
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
