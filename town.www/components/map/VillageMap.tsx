"use client";

import { useEffect, useMemo, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import type { Feature, FeatureCollection } from "geojson";
import type { MapIndicator } from "@/lib/store/mapStore";
import type { VillageListItem } from "@/lib/types";
import { colorForGrade, colorForIndicator } from "@/lib/utils/tvi";

type VillageMapProps = {
  villages: VillageListItem[];
  onSelect: (code: string) => void;
  selectedCode: string | null;
  indicator?: MapIndicator;
};

export function VillageMap({ villages, onSelect, selectedCode, indicator = "tvi" }: VillageMapProps) {
  const [geoJson, setGeoJson] = useState<FeatureCollection | null>(null);
  const villageByCode = useMemo(
    () => new Map(villages.map((v) => [v.village_code, v])),
    [villages],
  );

  useEffect(() => {
    fetch("/geojson/chungbuk_emd.geojson")
      .then((r) => r.json())
      .then(setGeoJson)
      .catch(() => setGeoJson(null));
  }, []);

  const style = (feature?: Feature) => {
    const code = String(feature?.properties?.emd_code ?? "");
    const village = villageByCode.get(code);
    const fill = village
      ? indicator === "tvi"
        ? colorForGrade(village.tvi_grade, village.color_hex)
        : colorForIndicator(
            {
              tvi_score: village.tvi_score,
              elderly_rate: village.aging_ratio ?? undefined,
              bus_interval_minutes: village.bus_interval_score != null ? village.bus_interval_score * 60 : null,
              nearest_stop_distance_m: village.nearest_stop_distance_m,
              bus_stops_within_1km: undefined,
            },
            indicator,
          )
      : "#e2e8f0";
    const selected = code === selectedCode;
    return {
      fillColor: fill,
      weight: selected ? 2 : 1,
      opacity: 1,
      color: selected ? "#1e3a8a" : "#64748b",
      fillOpacity: selected ? 0.75 : 0.55,
    };
  };

  const onEachFeature = (feature: Feature, layer: { bindTooltip: (s: string) => void; on: (e: object) => void }) => {
    const code = String(feature.properties?.emd_code ?? "");
    const village = villageByCode.get(code);
    const name = village?.village_name ?? feature.properties?.name ?? code;
    layer.bindTooltip(`${name}${village ? ` (TVI ${village.tvi_score})` : ""}`);
    layer.on({
      click: () => {
        if (code) onSelect(code);
      },
    });
  };

  return (
    <MapContainer center={[36.6, 127.5]} zoom={8} className="h-[480px] w-full rounded-xl z-0">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
      {geoJson && (
        <GeoJSON key={`${indicator}-${selectedCode}-${villages.length}`} data={geoJson} style={style} onEachFeature={onEachFeature} />
      )}
    </MapContainer>
  );
}
