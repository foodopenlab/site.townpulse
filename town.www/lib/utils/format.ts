import type { TviGrade } from "@/lib/types";

const LABELS: Record<TviGrade, string> = {
  danger: "소멸위험",
  warning: "주의",
  safe: "양호",
};

const COLORS: Record<TviGrade, string> = {
  danger: "#E74C3C",
  warning: "#F39C12",
  safe: "#27AE60",
};

export function tviLabel(grade: TviGrade) {
  return LABELS[grade];
}

export function tviColor(grade: TviGrade) {
  return COLORS[grade];
}

export function formatBudget(min: number, max: number) {
  if (min === max) return `${min.toLocaleString()}만원`;
  return `${min.toLocaleString()}~${max.toLocaleString()}만원`;
}

export function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}
