import { useState } from "react";
import { Button } from "@/components/ui/button";
import { syncRun, unsyncRun } from "@/lib/api";
import { toast } from "sonner";

interface SyncButtonProps {
  runId: string;
  isSynced: boolean;
  onDone?: () => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function SyncButton({ runId, isSynced, onDone, onLoadingChange }: SyncButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (loading) return;
    setLoading(true);
    onLoadingChange?.(true);
    try {
      if (isSynced) {
        const res = await unsyncRun(runId);
        toast.success(res.message || "Removed from Google Calendar");
      } else {
        const res = await syncRun(runId);
        toast.success(res.message || "Synced to Google Calendar");
      }
      onDone?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Operation failed";
      toast.error(msg);
    } finally {
      setLoading(false);
      onLoadingChange?.(false);
    }
  };

  return (
    <Button
      size="sm"
      variant={isSynced ? "outline" : "default"}
      onClick={handleClick}
      disabled={loading}
    >
      {loading
        ? isSynced
          ? "Removing..."
          : "Syncing..."
        : isSynced
          ? "Remove from Google Calendar"
          : "Sync to Google Calendar"}
    </Button>
  );
}
