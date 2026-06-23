import type { TviGrade } from "@/lib/types";
import { tviLabel } from "@/lib/utils/format";

const styles: Record<TviGrade, string> = {
  danger: "bg-danger/15 text-danger border-danger/30",
  warning: "bg-warning/15 text-warning border-warning/30",
  safe: "bg-safe/15 text-safe border-safe/30",
};

export function Badge({ grade }: { grade: TviGrade }) {
  return (
    <span className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${styles[grade]}`}>
      {tviLabel(grade)}
    </span>
  );
}
