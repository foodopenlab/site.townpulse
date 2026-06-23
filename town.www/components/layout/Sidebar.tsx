"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, LayoutDashboard, Map, MapPin, Sparkles } from "lucide-react";
import { sidebarItems } from "@/lib/config/navigation";

const iconByHref: Record<string, typeof LayoutDashboard> = {
  "/dashboard": LayoutDashboard,
  "/map": Map,
};

function NavIcon({ href }: { href: string }) {
  if (href === "/map/detail" || /^\/map\/\d+/.test(href)) return <MapPin size={18} />;
  if (href.startsWith("/prescription")) return <Sparkles size={18} />;
  if (href.startsWith("/report")) return <FileText size={18} />;
  const Icon = iconByHref[href] ?? LayoutDashboard;
  return <Icon size={18} />;
}

function NavLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
        active
          ? "border-l-[3px] border-accent bg-secondary font-medium text-primary"
          : "border-l-[3px] border-transparent hover:bg-muted"
      }`}
    >
      <NavIcon href={href} />
      {label}
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-card p-4 md:block">
      <nav className="space-y-1">
        {sidebarItems.map(({ href, label, isActive }) => (
          <NavLink key={href} href={href} label={label} active={isActive(pathname)} />
        ))}
      </nav>
    </aside>
  );
}

export function BottomNav() {
  const pathname = usePathname();
  const mobileItems = sidebarItems.map((item) => ({
    ...item,
    label: item.shortLabel ?? item.label.replace("소멸위험 ", "").replace(" 추천", "").replace(" 생성", ""),
  }));

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex border-t border-border bg-card md:hidden">
      {mobileItems.map(({ href, label, isActive }) => (
        <Link
          key={href}
          href={href}
          className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] ${
            isActive(pathname) ? "text-primary" : "text-muted-foreground"
          }`}
        >
          <NavIcon href={href} />
          <span className="truncate px-0.5">{label}</span>
        </Link>
      ))}
    </nav>
  );
}
