import type { DangerVillageSnap, TviGrade } from "@/lib/types";

export function getRiskSummary(snap: DangerVillageSnap): string {
  const reasons: string[] = [];

  if (snap.annual_pop_change_rate != null && snap.annual_pop_change_rate < -1) {
    reasons.push("인구 급감");
  }
  if (snap.net_youth_migration != null && snap.net_youth_migration < 0) {
    reasons.push(snap.net_youth_migration <= -5 ? "청년 유출 심각" : "청년 유출");
  }
  if (snap.bus_interval_score === 0) {
    reasons.push("교통 공백");
  }
  if (snap.vacancy_score != null && snap.vacancy_score < 40) {
    reasons.push("빈집 밀집");
  }
  if (snap.aging_ratio != null && snap.aging_ratio > 0.4) {
    reasons.push("고령화율 최상위");
  }

  return reasons.slice(0, 3).join(" · ") || "복합 위험 요인";
}

export const TVI_GRADE_LABELS: Record<TviGrade, string> = {
  danger: "위험",
  warning: "주의",
  safe: "안전",
};

export const TVI_GRADE_COLORS: Record<TviGrade, string> = {
  danger: "#E74C3C",
  warning: "#F39C12",
  safe: "#27AE60",
};

export function gradeFromScore(score: number): TviGrade {
  if (score < 30) return "danger";
  if (score < 60) return "warning";
  return "safe";
}

export function snapFromListItem(v: {
  tvi_grade?: TviGrade;
  bus_interval_score?: number | null;
  annual_pop_change_rate?: number | null;
  net_youth_migration?: number | null;
  vacancy_score?: number | null;
  aging_ratio?: number | null;
}): DangerVillageSnap {
  return {
    annual_pop_change_rate: v.annual_pop_change_rate,
    net_youth_migration: v.net_youth_migration,
    bus_interval_score: v.bus_interval_score ?? undefined,
    vacancy_score: v.vacancy_score,
    aging_ratio: v.aging_ratio,
  };
}
