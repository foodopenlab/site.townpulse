import { LayoutDashboard, Map, Sparkles, FileText } from "lucide-react";
import { DemoLink } from "@/components/landing/DemoLink";
import { DEMO_VILLAGE_CODE } from "@/lib/config/demo";

const features = [
  {
    icon: LayoutDashboard,
    title: "TVI 위험 지수",
    desc: "인구·빈집·교통 지표를 종합한 마을생존지수로 위험 순위를 한눈에",
    href: "/dashboard",
  },
  {
    icon: Map,
    title: "소멸위험 지도",
    desc: "충북 읍면동 지도에서 위험 지역을 시각적으로 파악하고 필터링",
    href: "/map",
  },
  {
    icon: Sparkles,
    title: "AI 처방 추천",
    desc: "마을 데이터를 분석해 빈집 활용·DRT·귀농 정착 등 맞춤 처방 제안",
    href: `/prescription/${DEMO_VILLAGE_CODE}`,
  },
  {
    icon: FileText,
    title: "PDF 리포트",
    desc: "보고서·회의 자료로 바로 쓸 수 있는 마을별 분석 리포트 생성",
    href: `/report/${DEMO_VILLAGE_CODE}`,
  },
];

export function FeatureSection() {
  return (
    <section className="mx-auto max-w-2xl px-4 py-10 md:px-8">
      <p className="text-xs font-medium uppercase tracking-wide text-primary">주요 기능</p>
      <h2 className="mt-2 text-xl font-bold">의사결정에 필요한 모든 것</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        공무원이 현장에서 바로 쓸 수 있도록 복잡한 데이터를 한 화면에 정리했습니다
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {features.map(({ icon: Icon, title, desc, href }) => (
          <DemoLink
            key={href}
            href={href}
            className="rounded-xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/50"
          >
            <Icon className="mb-2 h-5 w-5 text-primary" />
            <h3 className="text-sm font-semibold">{title}</h3>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{desc}</p>
          </DemoLink>
        ))}
      </div>
    </section>
  );
}
