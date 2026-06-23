"use client";

import Link from "next/link";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { gnbItems } from "@/lib/config/navigation";
import { logout } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/authStore";

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    useAuthStore.getState().hydrate();
  }, [pathname]);

  const onLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <header className="flex items-center justify-between gap-4 border-b border-border bg-card px-4 py-3">
      <Link href="/" className="shrink-0 text-lg font-bold text-primary">
        TownPulse
      </Link>
      <nav className="hidden flex-1 items-center justify-center gap-1 lg:flex">
        {gnbItems.map(({ href, label, isActive }) => (
          <Link
            key={href}
            href={href}
            className={`rounded-lg px-3 py-1.5 text-sm ${
              isActive(pathname) ? "bg-secondary font-medium text-primary" : "text-muted-foreground hover:bg-muted"
            }`}
          >
            {label}
          </Link>
        ))}
      </nav>
      <div className="flex shrink-0 items-center gap-2">
        <ThemeToggle />
        {token ? (
          <button
            type="button"
            onClick={onLogout}
            className="rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted"
          >
            로그아웃
          </button>
        ) : (
          <Link
            href="/login"
            className="rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-white hover:opacity-90"
          >
            로그인
          </Link>
        )}
      </div>
    </header>
  );
}
