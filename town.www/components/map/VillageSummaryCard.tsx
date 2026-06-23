import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import type { TviGrade, VillageMapSummary } from "@/lib/types";

export function VillageSummaryCard({ selected }: { selected: VillageMapSummary }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">{selected.village_name}</h2>
        <Badge grade={selected.tvi_grade as TviGrade} />
      </div>
      <p>TVI: {selected.tvi_score}</p>
      <p>최근접 정류장: {selected.nearest_stop_distance_m ?? "-"}m</p>
      <p>1km 내 정류장: {selected.bus_stops_within_1km ?? "-"}개</p>
      <Link href={`/map/${selected.village_code}`} className="text-primary underline">
        상세 보기
      </Link>
    </div>
  );
}
