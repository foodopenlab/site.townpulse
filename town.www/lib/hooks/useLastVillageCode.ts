"use client";

import { useCallback, useSyncExternalStore } from "react";
import { getLastVillageCode, setLastVillageCode as persistLastVillageCode } from "@/lib/village/lastVillage";

function subscribe(callback: () => void) {
  window.addEventListener("townpulse:village-changed", callback);
  return () => window.removeEventListener("townpulse:village-changed", callback);
}

function getSnapshot() {
  return getLastVillageCode();
}

function getServerSnapshot() {
  return null;
}

export function useLastVillageCode() {
  const code = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const setCode = useCallback((next: string) => {
    persistLastVillageCode(next);
    window.dispatchEvent(new Event("townpulse:village-changed"));
  }, []);

  return { code, setCode };
}
