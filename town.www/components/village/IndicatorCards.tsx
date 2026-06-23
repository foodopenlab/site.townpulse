import { formatPercent } from "@/lib/utils/format";
import type { VillageDetail } from "@/lib/types";

export function IndicatorCards({ detail }: { detail: VillageDetail }) {
  const indicators = [
    { label: "빈집률", value: formatPercent(detail.vacant_house_rate) },
    { label: "고령화율", value: formatPercent(detail.elderly_rate) },
    { label: "배차간격", value: detail.bus_interval_minutes ? `${detail.bus_interval_minutes}분` : "-" },
    {
      label: "정류장 거리",
      value: detail.nearest_stop_distance_m ? `${detail.nearest_stop_distance_m}m` : "-",
      badge: transportBadge(detail),
    },
    { label: "인구변화", value: formatPercent(detail.population_change_rate) },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
      {indicators.map((i) => (
        <div key={i.label} className="rounded-lg border border-border bg-card p-3">
          <p className="text-xs text-muted-foreground">{i.label}</p>
          <p className="text-lg font-semibold">{i.value}</p>
          {i.badge}
        </div>
      ))}
    </div>
  );
}

function transportBadge(detail: VillageDetail) {
  const isPartial = detail.snap_transport?.bus_route_count == null;
  const confirmedGap =
    !isPartial &&
    (detail.transport_gap ||
      detail.bus_stops_within_1km === 0 ||
      (detail.nearest_stop_distance_m != null && detail.nearest_stop_distance_m > 1000));

  if (isPartial) {
    return (
      <span className="mt-1 inline-block rounded bg-muted px-2 py-0.5 text-[10px] text-muted-foreground">
        교통 데이터 제한적
      </span>
    );
  }
  if (confirmedGap) {
    return (
      <span className="mt-1 inline-block rounded bg-danger/15 px-2 py-0.5 text-[10px] text-danger">
        교통 공백
      </span>
    );
  }
  return null;
}

export function TransportBadges({ detail }: { detail: VillageDetail }) {
  const isPartial = detail.snap_transport?.bus_route_count == null;
  const confirmedGap =
    !isPartial &&
    (detail.transport_gap ||
      detail.bus_stops_within_1km === 0 ||
      (detail.nearest_stop_distance_m != null && detail.nearest_stop_distance_m > 1000));

  return (
    <>
      {isPartial && (
        <span className="rounded bg-muted px-2 py-1 text-xs text-muted-foreground">교통 데이터 제한적</span>
      )}
      {confirmedGap && (
        <span className="rounded bg-danger/15 px-2 py-1 text-xs text-danger">교통 공백</span>
      )}
    </>
  );
}
