import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { uploadMmfCsv, type UploadMmfCsvResponse } from "@/lib/api";
import { notifyError, notifySuccess } from "@/lib/errors";
import { invalidateAllDash } from "@/lib/invalidate";
import { useDashboardStore } from "@/store";
import { cn } from "@/lib/utils";

interface MMFUploadButtonProps {
  onUploadComplete?: (data: UploadMmfCsvResponse) => void;
}

export function MMFUploadButton({ onUploadComplete }: MMFUploadButtonProps) {
  const { isAuthenticated } = useDashboardStore();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [lastUpload, setLastUpload] = useState<Date | null>(null);

  const uploadMutation = useMutation({
    mutationFn: ({ file, timezone }: { file: File; timezone?: string }) =>
      uploadMmfCsv(file, timezone),
    onSuccess: (data) => {
      // Targeted invalidation for dashboard data
      invalidateAllDash(queryClient);
      setLastUpload(new Date(data.updated_at));
      notifySuccess(data.message || "MMF data uploaded successfully");
      onUploadComplete?.(data);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    onError: (error) => {
      console.error("Failed to upload MMF data:", error);
      notifyError(error, "Failed to upload MMF data");
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadMutation.mutate({ file });
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const formatLastUpload = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 1) {
      return "Just now";
    } else if (diffMins < 60) {
      return `${diffMins} min${diffMins === 1 ? "" : "s"} ago`;
    } else {
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) {
        return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
      } else {
        return date.toLocaleDateString();
      }
    }
  };

  // Don't show upload button if user is not logged in
  if (!isAuthenticated) return null;

  const button = (
    <Button
      onClick={handleButtonClick}
      disabled={uploadMutation.isPending}
      variant="outline"
      size="sm"
    >
      {uploadMutation.isPending ? (
        <>
          <svg
            className="animate-spin h-4 w-4 mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          Uploading MMF...
        </>
      ) : (
        <>
          <svg
            className="h-4 w-4 mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          Upload MMF CSV
        </>
      )}
    </Button>
  );

  return (
    <TooltipProvider>
      <div className="flex flex-col items-end gap-1">
        {button}
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Upload MMF CSV file"
        />
        {lastUpload && (
          <span className="text-xs text-muted-foreground">
            Last uploaded {formatLastUpload(lastUpload)}
          </span>
        )}
        {uploadMutation.isError && (
          <span className="text-xs text-destructive">
            Failed to upload MMF data
          </span>
        )}
      </div>
    </TooltipProvider>
  );
}
