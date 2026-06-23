import type { TviGrade } from "@/lib/types";

export const TVI_GRADE_COLORS: Record<TviGrade, string> = {
  danger: "#dc2626",
  warning: "#f59e0b",
  safe: "#16a34a",
};

export function colorForGrade(grade: TviGrade | string | undefined, fallback = "#94a3b8") {
  if (grade === "danger" || grade === "warning" || grade === "safe") {
    return TVI_GRADE_COLORS[grade];
  }
  return fallback;
}

export function colorForIndicator(
  village: {
    tvi_score?: number;
    vacant_house_rate?: number;
    elderly_rate?: number;
    bus_interval_minutes?: number | null;
    nearest_stop_distance_m?: number | null;
    bus_stops_within_1km?: number | null;
  },
  indicator: string,
): string {
  switch (indicator) {
    case "vacant":
      return village.vacant_house_rate && village.vacant_house_rate > 0.15 ? "#dc2626" : "#16a34a";
    case "elderly":
      return village.elderly_rate && village.elderly_rate > 0.3 ? "#dc2626" : "#f59e0b";
    case "bus":
      return village.bus_interval_minutes && village.bus_interval_minutes > 40 ? "#dc2626" : "#16a34a";
    case "stop_access": {
      const gap =
        village.nearest_stop_distance_m != null &&
        (village.nearest_stop_distance_m > 1000 || (village.bus_stops_within_1km ?? 0) === 0);
      return gap ? "#dc2626" : "#16a34a";
    }
    case "tvi":
    default:
      if ((village.tvi_score ?? 100) < 40) return TVI_GRADE_COLORS.danger;
      if ((village.tvi_score ?? 100) < 70) return TVI_GRADE_COLORS.warning;
      return TVI_GRADE_COLORS.safe;
  }
}
