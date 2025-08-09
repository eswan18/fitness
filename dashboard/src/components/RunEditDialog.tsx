import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import type { Run, RunWithShoes } from "@/lib/api";
import { updateRun, fetchShoes, type UpdateRunRequest, type Shoe } from "@/lib/api";

interface RunEditDialogProps {
  run: Run | RunWithShoes | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onRunUpdated?: () => void; // Callback to refresh data
}

export function RunEditDialog({ run, open, onOpenChange, onRunUpdated }: RunEditDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shoes, setShoes] = useState<Shoe[]>([]);
  
  // Form state
  const [formData, setFormData] = useState({
    distance: "",
    duration: "", // Will store as "MM:SS" format
    avg_heart_rate: "",
    type: "",
    shoe_id: "",
    datetime_utc: "",
    change_reason: "",
  });

  // Load shoes on dialog open
  useEffect(() => {
    if (open) {
      fetchShoes()
        .then(setShoes)
        .catch((err) => {
          console.error("Failed to fetch shoes:", err);
          toast.error("Failed to load shoes");
        });
    }
  }, [open]);

  // Initialize form when run changes
  useEffect(() => {
    if (run && open) {
      // Format duration from seconds to MM:SS
      const minutes = Math.floor(run.duration / 60);
      const seconds = Math.floor(run.duration % 60);
      const durationString = `${minutes}:${seconds.toString().padStart(2, "0")}`;
      
      // Format datetime for input to match what table shows (local time)
      let datetimeString = "";
      if (run.datetime) {
        // Get local time components (same as what date-fns format displays)
        const year = run.datetime.getFullYear();
        const month = String(run.datetime.getMonth() + 1).padStart(2, '0');
        const day = String(run.datetime.getDate()).padStart(2, '0');
        const hours = String(run.datetime.getHours()).padStart(2, '0');
        const minutes = String(run.datetime.getMinutes()).padStart(2, '0');
        
        datetimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
      }
      
      // Get shoe_id from run (prefer shoe_id if available, otherwise find by name)
      let shoeId = "";
      if ("shoe_id" in run && run.shoe_id) {
        shoeId = run.shoe_id;
      }
      
      setFormData({
        distance: run.distance.toString(),
        duration: durationString,
        avg_heart_rate: run.avg_heart_rate?.toString() ?? "",
        type: run.type,
        shoe_id: shoeId,
        datetime_utc: datetimeString,
        change_reason: "",
      });
    }
  }, [run, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!run) return;

    // Check if run has ID (is RunWithShoes)
    const runId = "id" in run ? run.id : null;
    if (!runId) {
      toast.error("Cannot edit this run - missing ID");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Build update request with only changed fields
      const updateRequest: UpdateRunRequest = {
        changed_by: "user", // TODO: Get actual user ID/name
        change_reason: formData.change_reason.trim() || undefined,
      };

      // Parse and validate form data
      const currentDistance = parseFloat(formData.distance);
      if (!isNaN(currentDistance) && currentDistance !== run.distance) {
        if (currentDistance <= 0) {
          toast.error("Please enter a valid distance");
          return;
        }
        updateRequest.distance = currentDistance;
      } else if (isNaN(currentDistance) && formData.distance.trim() !== "") {
        toast.error("Please enter a valid distance");
        return;
      }

      // Parse duration from MM:SS to seconds
      const [minutes, seconds] = formData.duration.split(":").map(Number);
      const totalSeconds = (minutes || 0) * 60 + (seconds || 0);
      if (totalSeconds !== run.duration) {
        if (totalSeconds <= 0) {
          toast.error("Please enter a valid duration");
          return;
        }
        updateRequest.duration = totalSeconds;
      }

      // Handle heart rate changes with proper float comparison
      const currentHeartRate = formData.avg_heart_rate.trim() === "" 
        ? null 
        : parseFloat(formData.avg_heart_rate);
      
      if (currentHeartRate !== run.avg_heart_rate) {
        if (currentHeartRate === null) {
          updateRequest.avg_heart_rate = null;
        } else {
          if (isNaN(currentHeartRate) || currentHeartRate < 40 || currentHeartRate > 220) {
            toast.error("Please enter a valid heart rate (40-220)");
            return;
          }
          updateRequest.avg_heart_rate = currentHeartRate;
        }
      }

      if (formData.type !== run.type) {
        updateRequest.type = formData.type as "Outdoor Run" | "Treadmill Run";
      }

      // Handle shoe changes
      const currentShoeId = ("shoe_id" in run ? run.shoe_id : null) ?? "";
      if (formData.shoe_id !== currentShoeId) {
        updateRequest.shoe_id = formData.shoe_id || null;
      }

      // Handle datetime changes - convert local time input back to UTC
      if (formData.datetime_utc && run.datetime) {
        // Parse the datetime-local input as local time (natural interpretation)
        const inputAsLocalTime = new Date(formData.datetime_utc);
        
        if (inputAsLocalTime.getTime() !== run.datetime.getTime()) {
          updateRequest.datetime_utc = inputAsLocalTime.toISOString();
        }
      }

      // Only submit if there are actual changes
      const hasChanges = Object.keys(updateRequest).some(
        key => key !== "changed_by" && key !== "change_reason"
      );

      if (!hasChanges) {
        toast.info("No changes made");
        onOpenChange(false);
        return;
      }

      await updateRun(runId, updateRequest);
      
      toast.success("Run updated successfully!");
      onRunUpdated?.(); // Refresh data
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to edit run:", error);
      toast.error(
        error instanceof Error ? error.message : "Failed to update run"
      );
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
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Run</DialogTitle>
            <DialogDescription>
              Edit the details for your run from{" "}
              {run.date.toLocaleDateString()}.
              <br />
              <span className="text-xs text-muted-foreground mt-1 block">
                Source: {run.source}
              </span>
            </DialogDescription>
          </DialogHeader>

          <div className="py-4 space-y-4">
            {/* Distance */}
            <div className="space-y-2">
              <Label htmlFor="distance">Distance (miles)</Label>
              <Input
                id="distance"
                type="number"
                step="any"
                min="0"
                value={formData.distance}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, distance: e.target.value }))
                }
                placeholder="5.0"
                required
              />
            </div>

            {/* Duration */}
            <div className="space-y-2">
              <Label htmlFor="duration">Duration (MM:SS)</Label>
              <Input
                id="duration"
                type="text"
                pattern="[0-9]+:[0-9]{2}"
                value={formData.duration}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, duration: e.target.value }))
                }
                placeholder="30:00"
                title="Enter duration as MM:SS (e.g., 30:00 for 30 minutes)"
                required
              />
              <p className="text-xs text-muted-foreground">
                Format: minutes:seconds (e.g., 30:00 for 30 minutes)
              </p>
            </div>

            {/* Heart Rate */}
            <div className="space-y-2">
              <Label htmlFor="heart_rate">Average Heart Rate (bpm)</Label>
              <Input
                id="heart_rate"
                type="number"
                step="0.1"
                min="40"
                max="220"
                value={formData.avg_heart_rate}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    avg_heart_rate: e.target.value,
                  }))
                }
                placeholder="Optional"
              />
            </div>

            {/* Run Type */}
            <div className="space-y-2">
              <Label htmlFor="type">Run Type</Label>
              <Select
                value={formData.type}
                onValueChange={(value) =>
                  setFormData((prev) => ({ ...prev, type: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select run type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Outdoor Run">Outdoor Run</SelectItem>
                  <SelectItem value="Treadmill Run">Treadmill Run</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Shoes */}
            <div className="space-y-2">
              <Label htmlFor="shoes">Shoes</Label>
              <Select
                value={formData.shoe_id || "none"}
                onValueChange={(value) =>
                  setFormData((prev) => ({ 
                    ...prev, 
                    shoe_id: value === "none" ? "" : value 
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select shoes (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No shoes selected</SelectItem>
                  {shoes.map((shoe) => (
                    <SelectItem key={shoe.id} value={shoe.id}>
                      {shoe.name}
                      {shoe.retired_at && " (Retired)"}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Start Time */}
            {run.datetime && (
              <div className="space-y-2">
                <Label htmlFor="datetime">Start Time (Local)</Label>
                <Input
                  id="datetime"
                  type="datetime-local"
                  value={formData.datetime_utc}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      datetime_utc: e.target.value,
                    }))
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Displayed in your local timezone. Adjust if your GPS watch had the wrong time.
                </p>
              </div>
            )}

            {/* Change Reason */}
            <div className="space-y-2">
              <Label htmlFor="reason">Reason for Changes (optional)</Label>
              <Textarea
                id="reason"
                value={formData.change_reason}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    change_reason: e.target.value,
                  }))
                }
                placeholder="e.g., GPS accuracy issue, forgot to start watch"
                rows={2}
              />
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