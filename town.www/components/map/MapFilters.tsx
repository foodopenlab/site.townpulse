"use client";

import type { MapIndicator } from "@/lib/store/mapStore";

const SIGUN_OPTIONS = [
  "",
  "청주시",
  "충주시",
  "제천시",
  "보은군",
  "옥천군",
  "영동군",
  "증평군",
  "진천군",
  "괴산군",
  "음성군",
  "단양군",
];

const INDICATOR_OPTIONS: { value: MapIndicator; label: string }[] = [
  { value: "tvi", label: "TVI" },
  { value: "vacant", label: "빈집" },
  { value: "elderly", label: "고령" },
  { value: "bus", label: "배차" },
  { value: "stop_access", label: "정류장 접근" },
];

type MapFiltersProps = {
  grade: string;
  sigun: string;
  indicator: MapIndicator;
  onGradeChange: (v: string) => void;
  onSigunChange: (v: string) => void;
  onIndicatorChange: (v: MapIndicator) => void;
};

export function MapFilters({
  grade,
  sigun,
  indicator,
  onGradeChange,
  onSigunChange,
  onIndicatorChange,
}: MapFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <select
        className="rounded border border-border px-2 py-1 text-sm"
        value={grade}
        onChange={(e) => onGradeChange(e.target.value)}
        aria-label="위험 등급"
      >
        <option value="">전체 등급</option>
        <option value="danger">소멸위험</option>
        <option value="warning">주의</option>
        <option value="safe">양호</option>
      </select>
      <select
        className="rounded border border-border px-2 py-1 text-sm"
        value={sigun}
        onChange={(e) => onSigunChange(e.target.value)}
        aria-label="시군"
      >
        <option value="">전체 시군</option>
        {SIGUN_OPTIONS.filter(Boolean).map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <select
        className="rounded border border-border px-2 py-1 text-sm"
        value={indicator}
        onChange={(e) => onIndicatorChange(e.target.value as MapIndicator)}
        aria-label="지표"
      >
        {INDICATOR_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
