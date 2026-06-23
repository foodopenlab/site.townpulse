"use client";

import Link from "next/link";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { useStartDemo } from "@/lib/hooks/useStartDemo";

export function LandingNav() {
  const startDemo = useStartDemo();

  return (
    <nav className="flex items-center justify-between border-b border-border bg-card px-4 py-3 md:px-8">
      <Link href="/" className="text-lg font-bold text-primary">
        TownPulse
      </Link>
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <button
          type="button"
          onClick={() => startDemo()}
          className="rounded-lg border border-border px-3 py-1.5 text-sm hover:bg-muted"
        >
          데모 체험
        </button>
        <Link
          href="/login"
          className="rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-white hover:opacity-90"
        >
          로그인
        </Link>
      </div>
    </nav>
  );
}
