import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { Run } from "@/lib/api";

interface RunEditDialogProps {
  run: Run | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RunEditDialog({ run, open, onOpenChange }: RunEditDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!run) return;
    
    setIsSubmitting(true);
    
    try {
      // TODO: Implement actual edit functionality
      console.log("TODO: Edit run", run.date.toISOString());
      
      // Close dialog on success
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to edit run:", error);
      // TODO: Show error toast/message
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  // Reset form when dialog closes
  const handleOpenChange = (open: boolean) => {
    onOpenChange(open);
    if (!open) {
      // Reset any form state when dialog closes
      setIsSubmitting(false);
    }
  };

  if (!run) return null;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Run</DialogTitle>
            <DialogDescription>
              Edit the details for your run from{" "}
              {run.date.toLocaleDateString()}.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="space-y-4">
              {/* Placeholder content for now */}
              <div className="text-sm text-muted-foreground">
                <div><strong>Distance:</strong> {run.distance} miles</div>
                <div><strong>Duration:</strong> {Math.floor(run.duration / 60)}:{(run.duration % 60).toString().padStart(2, '0')}</div>
                <div><strong>Type:</strong> {run.type}</div>
                <div><strong>Source:</strong> {run.source}</div>
                {run.avg_heart_rate && (
                  <div><strong>Heart Rate:</strong> {run.avg_heart_rate} bpm</div>
                )}
                {run.shoes && (
                  <div><strong>Shoes:</strong> {run.shoes}</div>
                )}
              </div>
              
              <div className="text-sm text-amber-600 bg-amber-50 dark:bg-amber-950/20 dark:text-amber-400 p-3 rounded-md">
                🚧 Form fields coming soon! This dialog will include editable fields for distance, duration, heart rate, shoes, and start time.
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}