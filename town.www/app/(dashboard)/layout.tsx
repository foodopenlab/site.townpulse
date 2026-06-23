"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";
import { Header } from "@/components/layout/Header";
import { Sidebar, BottomNav } from "@/components/layout/Sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    useAuthStore.getState().hydrate();
    const token = useAuthStore.getState().token ?? localStorage.getItem("townpulse_token");
    if (!token) {
      router.replace("/");
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">
        로딩 중...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-auto p-4 pb-20 md:pb-4">{children}</main>
      </div>
      <BottomNav />
    </div>
  );
}
