import { Badge } from "@/components/ui/badge";
import { Info } from "lucide-react";
import type { SyncStatus } from "@/lib/api";

interface SyncStatusBadgeProps {
  status?: SyncStatus | null;
  errorMessage?: string | null;
}

export function SyncStatusBadge({ status, errorMessage }: SyncStatusBadgeProps) {
  if (!status) {
    return <Badge variant="outline">Not synced</Badge>;
  }

  if (status === "synced") {
    return <Badge variant="secondary">Synced</Badge>;
  }

  if (status === "pending") {
    return <Badge variant="secondary">Pending</Badge>;
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
