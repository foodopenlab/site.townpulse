export type TviGrade = "danger" | "warning" | "safe";

export interface VillageListItem {
  village_id: string;
  village_code: string;
  village_name: string;
  sigun_name: string;
  tvi_score: number;
  tvi_grade: TviGrade;
  tvi_label: string;
  color_hex: string;
  lat: number;
  lng: number;
  bus_interval_score?: number;
  nearest_stop_distance_m?: number;
  annual_pop_change_rate?: number | null;
  net_youth_migration?: number | null;
  vacancy_score?: number | null;
  aging_ratio?: number | null;
}

export interface VillageMapSummary {
  village_code: string;
  village_name: string;
  tvi_score: number;
  tvi_grade: TviGrade;
  nearest_stop_distance_m: number | null;
  bus_stops_within_1km: number | null;
}

export interface SnapTransport {
  bus_route_count: number | null;
  avg_bus_interval_min: number | null;
  nearest_stop_distance_m: number | null;
  bus_stops_within_1km: number | null;
  fetched_at: string;
}

export interface PrescriptionItem {
  id: string;
  rank: 1 | 2 | 3;
  code: string;
  title: string;
  description: string | null;
  budget_min: number;
  budget_max: number;
  tvi_gain_min: number;
  tvi_gain_max: number;
  fund_applicable: boolean;
  timeline: "urgent" | "medium" | "long";
}

export interface VillageDetail {
  village_id: string;
  village_code: string;
  village_name: string;
  sigun_name: string;
  tvi_score: number;
  tvi_grade: TviGrade;
  bus_interval_score: number;
  vacant_house_rate: number;
  elderly_rate: number;
  bus_interval_minutes: number | null;
  nearest_stop_distance_m: number | null;
  bus_stops_within_1km: number | null;
  transport_gap: boolean;
  population_change_rate: number;
  extinction_probability_5y: number;
  snap_transport?: SnapTransport;
  updated_at: string;
  prescriptions_preview?: PrescriptionItem[];
}

export interface DangerVillageSnap {
  annual_pop_change_rate?: number | null;
  net_youth_migration?: number | null;
  bus_interval_score?: number | null;
  vacancy_score?: number | null;
  aging_ratio?: number | null;
}

export interface DangerVillageItem extends DangerVillageSnap {
  village_code: string;
  village_name: string;
  sigun_name: string;
  tvi_score: number;
  tvi_grade?: TviGrade;
}

export interface DashboardSummary {
  total_villages: number;
  danger_count: number;
  warning_count: number;
  safe_count: number;
  total_vacant_houses: number;
  transport_gap_count: number;
  top5_danger_villages: DangerVillageItem[];
  grade_changed_this_month: number;
  pending_prescription_count: number;
}

export interface PrescriptionList {
  village_id: string;
  prescriptions: PrescriptionItem[];
  generated_at: string;
}
