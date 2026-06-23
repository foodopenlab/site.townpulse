import { formatBudget } from "@/lib/utils/format";
import type { PrescriptionItem } from "@/lib/types";

export function PrescriptionCard({
  item,
  onExplain,
  disabled,
}: {
  item: PrescriptionItem;
  onExplain: () => void;
  disabled?: boolean;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-sm text-muted-foreground">{item.rank}순위</p>
      <h2 className="font-semibold">{item.title}</h2>
      <p className="mt-2 text-sm">
        예상 TVI +{Number(item.tvi_gain_min).toFixed(1)}~{Number(item.tvi_gain_max).toFixed(1)}
      </p>
      <p className="text-sm">{formatBudget(item.budget_min, item.budget_max)}</p>
      <button
        type="button"
        onClick={onExplain}
        className="mt-3 rounded bg-primary px-3 py-1 text-sm text-white disabled:opacity-60"
        disabled={disabled}
      >
        AI 설명 보기
      </button>
    </div>
  );
}
