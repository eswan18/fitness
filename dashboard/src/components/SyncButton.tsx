import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useRunSync } from "@/hooks/useRunSync";

interface SyncButtonProps {
  runId: string;
  isSynced: boolean;
  onDone?: () => void;
  onLoadingChange?: (loading: boolean) => void;
}

export function SyncButton({
  runId,
  isSynced,
  onDone,
  onLoadingChange,
}: SyncButtonProps) {
  const [loading, setLoading] = useState(false);
  const { toggleSync } = useRunSync({
    onChanged: onDone,
    onLoadingChange: (id, l) => {
      if (id === runId) onLoadingChange?.(l);
    },
  });

  const handleClick = async () => {
    if (loading) return;
    setLoading(true);
    try {
      await toggleSync(runId, isSynced);
    } finally {
      setLoading(false);
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
