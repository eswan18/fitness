import { useState } from "react";
import { format } from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ShoeMileage } from "@/lib/api";
import { ShoeRetirementDialog } from "./ShoeRetirementDialog";

interface ShoeManagementDialogProps {
  shoes: ShoeMileage[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ShoeManagementDialog({
  shoes,
  open,
  onOpenChange,
}: ShoeManagementDialogProps) {
  const [selectedShoe, setSelectedShoe] = useState<ShoeMileage | null>(null);
  const [retirementDialogOpen, setRetirementDialogOpen] = useState(false);

  const handleManageShoe = (shoe: ShoeMileage) => {
    setSelectedShoe(shoe);
    setRetirementDialogOpen(true);
  };

  // Sort shoes: active first (by mileage), then retired (by mileage)
  const sortedShoes = [...shoes].sort((a, b) => {
    const aRetired = !!a.shoe.retired_at;
    const bRetired = !!b.shoe.retired_at;
    if (aRetired !== bRetired) {
      return aRetired ? 1 : -1; // Active shoes first
    }
    return b.mileage - a.mileage; // Higher mileage first within each group
  });

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Manage Shoes</DialogTitle>
            <DialogDescription>
              View and manage retirement status for all your shoes.
            </DialogDescription>
          </DialogHeader>

          <div className="mt-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Shoe</TableHead>
                  <TableHead className="text-right">Mileage</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Retirement Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedShoes.map((shoeData) => (
                  <TableRow key={shoeData.shoe.id}>
                    <TableCell className="font-medium max-w-[200px]">
                      <div className="truncate" title={shoeData.shoe.name}>
                        {shoeData.shoe.name}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      {shoeData.mileage.toFixed(1)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          shoeData.shoe.retired_at ? "secondary" : "default"
                        }
                        className={shoeData.shoe.retired_at ? "opacity-70" : ""}
                      >
                        {shoeData.shoe.retired_at ? "Retired" : "Active"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {shoeData.shoe.retired_at ? (
                        <span className="text-sm text-muted-foreground">
                          {format(
                            new Date(shoeData.shoe.retired_at),
                            "MMM d, yyyy",
                          )}
                        </span>
                      ) : (
                        <span className="text-sm text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleManageShoe(shoeData)}
                      >
                        {shoeData.shoe.retired_at ? "Manage" : "Retire"}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </DialogContent>
      </Dialog>

      <ShoeRetirementDialog
        shoe={selectedShoe}
        open={retirementDialogOpen}
        onOpenChange={setRetirementDialogOpen}
      />
    </>
  );
}
