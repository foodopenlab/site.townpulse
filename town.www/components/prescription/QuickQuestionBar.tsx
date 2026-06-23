const QUICK_QUESTIONS = [
  "예산 상세와 집행 순서를 알려주세요.",
  "행안부·도비 기금 매칭 가능 여부는?",
  "주민 설득 포인트를 정리해 주세요.",
  "유사 사례와 기대 효과를 비교해 주세요.",
];

export function QuickQuestionBar({
  onSelect,
  disabled,
}: {
  onSelect: (q: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUICK_QUESTIONS.map((q) => (
        <button
          key={q}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(q)}
          className="rounded-full border border-border bg-card px-3 py-1 text-xs hover:bg-muted disabled:opacity-50"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
