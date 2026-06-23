import { DemoLink } from "@/components/landing/DemoLink";
import { DEMO_VILLAGE_CODE } from "@/lib/config/demo";

const steps = [
  {
    title: "마을 검색 또는 지도에서 선택",
    desc: "충북 228개 읍면동을 지도에서 클릭하거나 이름으로 검색해 진입합니다",
    href: "/map",
  },
  {
    title: "TVI 위험 지수 및 원인 확인",
    desc: "인구 감소율·고령화·빈집·교통 점수를 한 화면에서 확인하고 주요 원인을 파악합니다",
    href: `/map/${DEMO_VILLAGE_CODE}`,
  },
  {
    title: "AI 처방 확인 후 리포트 생성",
    desc: "AI가 제안하는 처방과 예산 추정을 검토한 뒤 PDF 보고서로 바로 출력합니다",
    href: `/prescription/${DEMO_VILLAGE_CODE}`,
  },
];

export function HowToSection() {
  return (
    <section className="mx-auto max-w-2xl border-t border-border px-4 py-10 md:px-8">
      <p className="text-xs font-medium uppercase tracking-wide text-primary">사용 방법</p>
      <h2 className="mt-2 text-xl font-bold">3단계로 바로 시작</h2>
      <ol className="mt-6 space-y-0">
        {steps.map((step, i) => (
          <li key={step.href} className={i < steps.length - 1 ? "border-b border-border" : ""}>
            <DemoLink href={step.href} className="flex gap-4 py-4 transition-colors hover:bg-muted/30">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-medium text-white">
                {i + 1}
              </span>
              <div>
                <h3 className="text-sm font-semibold">{step.title}</h3>
                <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">{step.desc}</p>
              </div>
            </DemoLink>
          </li>
        ))}
      </ol>
    </section>
  );
}
