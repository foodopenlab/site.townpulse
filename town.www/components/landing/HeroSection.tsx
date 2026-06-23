"use client";

import Link from "next/link";
import { useStartDemo } from "@/lib/hooks/useStartDemo";

export function HeroSection() {
  const startDemo = useStartDemo();

  return (
    <section className="mx-auto max-w-2xl px-4 py-12 text-center md:px-8 md:py-16">
      <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-muted px-3 py-1 text-xs text-muted-foreground">
        <span className="h-1.5 w-1.5 rounded-full bg-safe" />
        충청북도 공식 파일럿 운영 중
      </div>
      <h1 className="text-3xl font-bold leading-snug md:text-4xl">
        충북 228개 마을,
        <br />
        <span className="text-primary">소멸위험을 AI로 진단합니다</span>
      </h1>
      <p className="mt-4 text-sm leading-relaxed text-muted-foreground md:text-base">
        인구·빈집·교통 데이터를 실시간 분석해
        <br className="hidden sm:inline" />
        마을별 위험 등급과 맞춤 처방을 제안합니다
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
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
