export type NavItem = {
  href: string;
  label: string;
  shortLabel?: string;
  isActive: (pathname: string) => boolean;
};

/** GNB — 처방·리포트는 선택 마을 기준 리다이렉트 경로 */
export const gnbItems: NavItem[] = [
  { href: "/dashboard", label: "대시보드", isActive: (p) => p === "/dashboard" },
  { href: "/map", label: "소멸위험 지도", isActive: (p) => p === "/map" },
  {
    href: "/prescription",
    label: "AI 처방",
    shortLabel: "처방",
    isActive: (p) => p.startsWith("/prescription"),
  },
  {
    href: "/report",
    label: "리포트",
    isActive: (p) => p.startsWith("/report"),
  },
];

/** 사이드바 — GNB + 마을 상세(마지막 선택 마을로 이동) */
export const sidebarItems: NavItem[] = [
  ...gnbItems.slice(0, 2),
  {
    href: "/map/detail",
    label: "마을 상세",
    isActive: (p) => /^\/map\/\d+/.test(p),
  },
  ...gnbItems.slice(2),
];
