import { useState } from "react";
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
import type { ShoeMileageWithRetirement } from "@/lib/api";

interface ShoeRetirementDialogProps {
  shoe: ShoeMileageWithRetirement | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ShoeRetirementDialog({
  shoe,
  open,
  onOpenChange,
}: ShoeRetirementDialogProps) {
  const [retirementDate, setRetirementDate] = useState<Date | undefined>(
    shoe?.retirement_date ? new Date(shoe.retirement_date) : new Date(),
  );
  const [notes, setNotes] = useState(shoe?.retirement_notes || "");

  const queryClient = useQueryClient();

  const retireMutation = useMutation({
    mutationFn: ({
      shoeName,
      request,
    }: {
      shoeName: string;
      request: { retirement_date: string; notes?: string };
    }) => retireShoe(shoeName, request),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["miles", "by-shoe-with-retirement"],
      });
      onOpenChange(false);
    },
  });

  const unretireMutation = useMutation({
    mutationFn: (shoeName: string) => unretireShoe(shoeName),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["miles", "by-shoe-with-retirement"],
      });
      onOpenChange(false);
    },
  });

  const handleRetire = () => {
    if (!shoe || !retirementDate) return;

    retireMutation.mutate({
      shoeName: shoe.shoe,
      request: {
        retirement_date: format(retirementDate, "yyyy-MM-dd"),
        notes: notes.trim() || undefined,
      },
    });
  };

  const handleUnretire = () => {
    if (!shoe) return;
    unretireMutation.mutate(shoe.shoe);
  };

  if (!shoe) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {shoe.retired ? "Manage Retired Shoe" : "Retire Shoe"}
          </DialogTitle>
          <DialogDescription>
            {shoe.retired
              ? `${shoe.shoe} is currently retired with ${shoe.mileage.toFixed(1)} miles.`
              : `Retire ${shoe.shoe} (${shoe.mileage.toFixed(1)} miles)?`}
          </DialogDescription>
        </DialogHeader>

        {!shoe.retired && (
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

        {shoe.retired && (
          <div className="py-4 space-y-2">
            <div>
              <Label className="text-sm font-medium">Retirement Date:</Label>
              <p className="text-sm text-muted-foreground">
                {shoe.retirement_date
                  ? format(new Date(shoe.retirement_date), "PPP")
                  : "Unknown"}
              </p>
            </div>
            {shoe.retirement_notes && (
              <div>
                <Label className="text-sm font-medium">Notes:</Label>
                <p className="text-sm text-muted-foreground">
                  {shoe.retirement_notes}
                </p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          {shoe.retired ? (
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
