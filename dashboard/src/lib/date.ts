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

// Format a Date into yyyy-MM-dd'T'HH:mm for datetime-local inputs
export function toLocalDateTimeInputValue(date: Date | undefined): string {
  if (!date || !isDate(date)) return "";
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}
