"use client";

import Link from "next/link";
import { DEMO_VILLAGE_CODE } from "@/lib/config/demo";
import { useStartDemo } from "@/lib/hooks/useStartDemo";

export function LandingCTA() {
  const startDemo = useStartDemo();

  return (
    <section className="mx-4 mb-12 rounded-xl border border-border bg-muted/50 p-8 text-center md:mx-auto md:max-w-2xl">
      <h2 className="text-lg font-bold">지금 바로 체험해보세요</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        로그인 없이 데모 모드로
        <br />
        단양군 영춘면({DEMO_VILLAGE_CODE}) 등 실제 분석 사례를 확인할 수 있습니다
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <button
          type="button"
          onClick={() => startDemo()}
          className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white hover:opacity-90"
        >
          데모로 시작하기
        </button>
        <Link
          href="/login"
          className="rounded-lg border border-border bg-card px-6 py-2.5 text-sm font-medium hover:bg-muted"
        >
          기관 로그인
        </Link>
      </div>
    </section>
  );
}
