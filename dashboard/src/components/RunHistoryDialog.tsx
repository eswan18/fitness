import { useState, useEffect, useCallback } from "react";
import { format } from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Clock, User, FileText, AlertCircle } from "lucide-react";
import type { RunWithShoes } from "@/lib/api";

interface RunHistoryRecord {
  history_id: number;
  run_id: string;
  version_number: number;
  change_type: string;
  datetime_utc: string;
  type: string;
  distance: number;
  duration: number;
  source: string;
  avg_heart_rate: number | null;
  shoe_id: string | null;
  changed_at: string;
  changed_by: string | null;
  change_reason: string | null;
}

interface RunHistoryDialogProps {
  run: RunWithShoes | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RunHistoryDialog({ run, open, onOpenChange }: RunHistoryDialogProps) {
  const [history, setHistory] = useState<RunHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!run) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/runs/${run.id}/history`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.statusText}`);
      }
      
      const historyData = await response.json();
      setHistory(historyData);
    } catch (err) {
      console.error("Error fetching run history:", err);
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  }, [run]);

  useEffect(() => {
    if (open && run) {
      fetchHistory();
    }
  }, [open, run, fetchHistory]);

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

  const getChangeTypeColor = (changeType: string) => {
    switch (changeType) {
      case "original":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "edit":
        return "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300";
      case "deletion":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };

  const getChangeTypeIcon = (changeType: string) => {
    switch (changeType) {
      case "original":
        return <FileText className="h-4 w-4" />;
      case "edit":
        return <Clock className="h-4 w-4" />;
      case "deletion":
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  // Helper function to parse UTC timestamps correctly and display in local time
  const parseUTCTimestamp = (timestamp: string): Date => {
    // Ensure the timestamp is treated as UTC by appending 'Z' if not present
    const utcString = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    return new Date(utcString);
  };

  if (!run) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit History</DialogTitle>
          <DialogDescription>
            Complete edit history for your run from {format(run.date, "MMM d, yyyy")}.
            <br />
            <span className="text-xs text-muted-foreground mt-1 block">
              Source: {run.source} • Current Distance: {run.distance.toFixed(2)} mi
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {loading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
              <p className="text-destructive">{error}</p>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-8 w-8 mx-auto mb-2" />
              <p>No edit history available for this run.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground mb-4">
                Showing {history.length} version{history.length !== 1 ? 's' : ''} (newest first)
              </div>
              
              {history.map((record, index) => (
                <div
                  key={record.history_id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Badge 
                        variant="secondary" 
                        className={`${getChangeTypeColor(record.change_type)} flex items-center gap-1`}
                      >
                        {getChangeTypeIcon(record.change_type)}
                        Version {record.version_number}
                      </Badge>
                      
                      <div className="text-sm text-muted-foreground">
                        {record.change_type === "original" ? "Original data" : "Edited"}
                      </div>
                      
                      {index === 0 && (
                        <Badge variant="outline" className="text-xs">
                          Current
                        </Badge>
                      )}
                    </div>
                    
                    <div className="text-xs text-muted-foreground text-right">
                      {format(parseUTCTimestamp(record.changed_at), "MMM d, yyyy")}
                      <br />
                      {format(parseUTCTimestamp(record.changed_at), "h:mm a")}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="font-medium text-muted-foreground">Distance</div>
                      <div>{record.distance.toFixed(3)} mi</div>
                    </div>
                    <div>
                      <div className="font-medium text-muted-foreground">Duration</div>
                      <div>{formatDuration(record.duration)}</div>
                    </div>
                    <div>
                      <div className="font-medium text-muted-foreground">Heart Rate</div>
                      <div>{record.avg_heart_rate ? `${Math.round(record.avg_heart_rate)} bpm` : "—"}</div>
                    </div>
                    <div>
                      <div className="font-medium text-muted-foreground">Start Time (Local)</div>
                      <div className="text-sm">
                        {format(parseUTCTimestamp(record.datetime_utc), "MMM d, yyyy")}
                        <br />
                        <span className="font-mono">{format(parseUTCTimestamp(record.datetime_utc), "h:mm:ss a")}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {record.changed_by && (
                      <div className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {record.changed_by}
                      </div>
                    )}
                    
                    {record.change_reason && (
                      <div className="flex-1">
                        <span className="font-medium">Reason:</span> {record.change_reason}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}