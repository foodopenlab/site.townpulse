"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { ensureDemoSession } from "@/lib/api/auth";

export function useStartDemo() {
  const router = useRouter();

  return useCallback(async () => {
    await ensureDemoSession();
    router.push("/dashboard");
  }, [router]);
}
