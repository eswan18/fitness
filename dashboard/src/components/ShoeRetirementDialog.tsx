import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { retireShoe, unretireShoe } from "@/lib/api";
import type { ShoeMileage } from "@/lib/api";

interface ShoeRetirementDialogProps {
  shoe: ShoeMileage | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ShoeRetirementDialog({
  shoe,
  open,
  onOpenChange,
}: ShoeRetirementDialogProps) {
  const [retirementDate, setRetirementDate] = useState<Date | undefined>(
    new Date(),
  );
  const [notes, setNotes] = useState("");

  // Reset form state when shoe changes or dialog opens
  useEffect(() => {
    if (shoe && open) {
      setRetirementDate(
        shoe.shoe.retired_at ? new Date(shoe.shoe.retired_at) : new Date(),
      );
      setNotes(shoe.shoe.retirement_notes || "");
    }
  }, [shoe, open]);

  const queryClient = useQueryClient();

  const retireMutation = useMutation({
    mutationFn: ({
      shoeId,
      request,
    }: {
      shoeId: string;
      request: { retired_at: string; retirement_notes?: string };
    }) => retireShoe(shoeId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["miles", "by-shoe", "include-retired"],
      });
      onOpenChange(false);
    },
  });

  const unretireMutation = useMutation({
    mutationFn: (shoeId: string) => unretireShoe(shoeId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["miles", "by-shoe", "include-retired"],
      });
      onOpenChange(false);
    },
  });

  const handleRetire = () => {
    if (!shoe || !retirementDate) return;

    retireMutation.mutate({
      shoeId: shoe.shoe.id,
      request: {
        retired_at: format(retirementDate, "yyyy-MM-dd"),
        retirement_notes: notes.trim() || undefined,
      },
    });
  };

  const handleUnretire = () => {
    if (!shoe) return;
    unretireMutation.mutate(shoe.shoe.id);
  };

  if (!shoe) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {shoe.shoe.retired_at ? "Manage Retired Shoe" : "Retire Shoe"}
          </DialogTitle>
          <DialogDescription>
            {shoe.shoe.retired_at
              ? `${shoe.shoe.name} is currently retired with ${shoe.mileage.toFixed(1)} miles.`
              : `Retire ${shoe.shoe.name} (${shoe.mileage.toFixed(1)} miles)?`}
          </DialogDescription>
        </DialogHeader>

        {!shoe.shoe.retired_at && (
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="retirement-date">Retirement Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "justify-start text-left font-normal",
                      !retirementDate && "text-muted-foreground",
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {retirementDate
                      ? format(retirementDate, "PPP")
                      : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={retirementDate}
                    onSelect={setRetirementDate}
                    initialFocus
                    defaultMonth={retirementDate}
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                placeholder="e.g., worn out, switched to new pair..."
                value={notes}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setNotes(e.target.value)
                }
                rows={3}
              />
            </div>
          </div>
        )}

        {shoe.shoe.retired_at && (
          <div className="py-4 space-y-2">
            <div>
              <Label className="text-sm font-medium">Retirement Date:</Label>
              <p className="text-sm text-muted-foreground">
                {shoe.shoe.retired_at
                  ? format(new Date(shoe.shoe.retired_at), "PPP")
                  : "Unknown"}
              </p>
            </div>
            {shoe.shoe.retirement_notes && (
              <div>
                <Label className="text-sm font-medium">Notes:</Label>
                <p className="text-sm text-muted-foreground">
                  {shoe.shoe.retirement_notes}
                </p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          {shoe.shoe.retired_at ? (
            <Button
              onClick={handleUnretire}
              disabled={unretireMutation.isPending}
            >
              {unretireMutation.isPending ? "Unretiring..." : "Unretire Shoe"}
            </Button>
          ) : (
            <Button
              onClick={handleRetire}
              disabled={!retirementDate || retireMutation.isPending}
            >
              {retireMutation.isPending ? "Retiring..." : "Retire Shoe"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
