export function toISODate(date: Date | undefined): string | undefined {
  if (!date) return undefined;
  // Ensure YYYY-MM-DD
  return date.toISOString().split("T")[0];
}

export function fromISODate(iso: string | undefined | null): Date | undefined {
  if (!iso) return undefined;
  const d = new Date(iso + (iso.includes("T") ? "" : "T00:00:00"));
  return isNaN(d.getTime()) ? undefined : d;
}

export function isDate(value: unknown): value is Date {
  return value instanceof Date && !isNaN(value.getTime());
}