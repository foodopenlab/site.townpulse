import { create } from "zustand";

export type MapIndicator = "tvi" | "vacant" | "elderly" | "bus" | "stop_access";

type MapState = {
  grade: string;
  sigun: string;
  indicator: MapIndicator;
  setGrade: (grade: string) => void;
  setSigun: (sigun: string) => void;
  setIndicator: (indicator: MapIndicator) => void;
};

export const useMapStore = create<MapState>((set) => ({
  grade: "",
  sigun: "",
  indicator: "tvi",
  setGrade: (grade) => set({ grade }),
  setSigun: (sigun) => set({ sigun }),
  setIndicator: (indicator) => set({ indicator }),
}));
