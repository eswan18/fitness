import { Badge } from "@/components/ui/badge";
import { Info, CalendarCheck, Clock } from "lucide-react";
import type { SyncStatus } from "@/lib/api";

interface SyncStatusBadgeProps {
  status?: SyncStatus | null;
  errorMessage?: string | null;
}

export function SyncStatusBadge({
  status,
  errorMessage,
}: SyncStatusBadgeProps) {
  if (!status) {
    return <Badge variant="outline">Not synced</Badge>;
  }

  if (status === "synced") {
    return (
      <Badge
        variant="outline"
        className="bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800"
      >
        <CalendarCheck className="h-3 w-3" /> Synced
      </Badge>
    );
  }

  if (status === "pending") {
    return (
      <Badge
        variant="outline"
        className="bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:border-amber-800"
      >
        <Clock className="h-3 w-3" /> Pending
      </Badge>
    );
  }

  // failed
  return (
    <Badge
      variant="destructive"
      title={errorMessage || "Sync failed. Click to retry from menu."}
      aria-label={errorMessage || "Sync failed"}
    >
      <Info className="inline h-3 w-3" /> Failed
    </Badge>
  );
}
