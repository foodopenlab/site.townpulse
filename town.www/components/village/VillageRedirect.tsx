"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { getLastVillageCode } from "@/lib/village/lastVillage";

type VillageRedirectTarget = "detail" | "prescription" | "report";

const paths: Record<VillageRedirectTarget, (code: string) => string> = {
  detail: (code) => `/map/${code}`,
  prescription: (code) => `/prescription/${code}`,
  report: (code) => `/report/${code}`,
};

export function VillageRedirect({ target }: { target: VillageRedirectTarget }) {
  const router = useRouter();

  useEffect(() => {
    const code = getLastVillageCode();
    router.replace(code ? paths[target](code) : "/map");
  }, [router, target]);

  return <LoadingSpinner />;
}
