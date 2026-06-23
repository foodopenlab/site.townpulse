const STORAGE_KEY = "townpulse_last_village_code";

export function getLastVillageCode(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEY);
}

export function setLastVillageCode(code: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, code);
  window.dispatchEvent(new Event("townpulse:village-changed"));
}

export function clearLastVillageCode() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event("townpulse:village-changed"));
}
