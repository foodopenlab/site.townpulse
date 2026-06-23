export function dedupePrescriptionsByRank<T extends { rank: number }>(items: T[]): T[] {
  const seen = new Set<number>();
  return items.filter((item) => {
    if (seen.has(item.rank)) return false;
    seen.add(item.rank);
    return true;
  });
}
